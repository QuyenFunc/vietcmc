from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta
from typing import Optional
import logging
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.database import get_db
from app.models import Client, Job
from app.schemas import ClientLoginRequest, ClientUpdateWebhookRequest, APIResponse
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

router = APIRouter()

# JWT settings
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(data: dict) -> str:
    """Create JWT token for client"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_client(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Client:
    """Get current client from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authorization header missing"}
        )
    
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id: int = payload.get("client_id")
        
        if client_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": "Invalid token"}
            )
        
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "CLIENT_NOT_FOUND", "message": "Client not found"}
            )
        
        return client
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Could not validate token"}
        )


@router.post("/client/login", response_model=APIResponse)
async def client_login(
    request: ClientLoginRequest,
    db: Session = Depends(get_db)
):
    """Login for client"""
    
    try:
        # Find client by email
        client = db.query(Client).filter(Client.email == request.email).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Incorrect email or password"
                }
            )
        
        # Verify password
        if not client.password_hash or not pwd_context.verify(request.password, client.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Incorrect email or password"
                }
            )
        
        # Check if client is active
        if client.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "CLIENT_SUSPENDED",
                    "message": "Your account has been suspended"
                }
            )
        
        # Create JWT token
        access_token = create_access_token({"client_id": client.id})
        
        logger.info(f"Client {client.email} logged in successfully")
        
        return APIResponse(
            success=True,
            data={
                "token": access_token,
                "client": {
                    "id": client.id,
                    "app_id": client.app_id,
                    "organization_name": client.organization_name,
                    "email": client.email,
                    "api_key": client.api_key,
                    "hmac_secret": client.hmac_secret,
                    "webhook_url": client.webhook_url,
                    "status": client.status,
                    "created_at": client.created_at.isoformat() if client.created_at else None
                }
            },
            message="Login successful"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during client login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Login failed"
            }
        )


@router.get("/client/stats", response_model=APIResponse)
async def get_client_stats(
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get statistics for current client"""
    
    try:
        # Jobs today
        today = date.today()
        jobs_today = db.query(Job).filter(
            Job.client_id == client.id,
            func.date(Job.created_at) == today
        ).count()
        
        # Total jobs
        total_jobs = db.query(Job).filter(Job.client_id == client.id).count()
        
        # Success rate
        completed_jobs = db.query(Job).filter(
            Job.client_id == client.id,
            Job.status == 'completed'
        ).count()
        
        failed_jobs = db.query(Job).filter(
            Job.client_id == client.id,
            Job.status == 'failed'
        ).count()
        
        if completed_jobs + failed_jobs > 0:
            success_rate = round((completed_jobs / (completed_jobs + failed_jobs)) * 100, 2)
        else:
            success_rate = 0
        
        # Average jobs per minute (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        jobs_last_hour = db.query(Job).filter(
            Job.client_id == client.id,
            Job.created_at >= one_hour_ago
        ).count()
        
        avg_per_minute = round(jobs_last_hour / 60, 2) if jobs_last_hour > 0 else 0
        
        return APIResponse(
            success=True,
            data={
                "jobs_today": jobs_today,
                "total_jobs": total_jobs,
                "success_rate": success_rate,
                "avg_per_minute": avg_per_minute,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs
            }
        )
    
    except Exception as e:
        logger.error(f"Error getting client stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Could not retrieve statistics"
            }
        )


@router.get("/client/jobs", response_model=APIResponse)
async def get_client_jobs(
    page: int = 1,
    per_page: int = 10,
    status_filter: Optional[str] = None,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get jobs list for current client"""
    
    try:
        query = db.query(Job).filter(Job.client_id == client.id)
        
        if status_filter:
            query = query.filter(Job.status == status_filter)
        
        total = query.count()
        
        jobs = query.order_by(desc(Job.created_at))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        return APIResponse(
            success=True,
            data={
                "jobs": [
                    {
                        "job_id": j.job_id,
                        "comment_id": j.comment_id,
                        "text": j.text[:100] + "..." if len(j.text) > 100 else j.text,
                        "status": j.status,
                        "sentiment": j.sentiment,
                        "moderation_result": j.moderation_result,
                        "confidence_score": float(j.confidence_score) if j.confidence_score else None,
                        "created_at": j.created_at.isoformat() if j.created_at else None,
                        "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                        "processing_duration_ms": j.processing_duration_ms
                    }
                    for j in jobs
                ],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            }
        )
    
    except Exception as e:
        logger.error(f"Error getting client jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Could not retrieve jobs list"
            }
        )


@router.options("/client/webhook")
async def webhook_options():
    """Handle CORS preflight for webhook endpoint"""
    return {"message": "OK"}


@router.put("/client/webhook", response_model=APIResponse)
async def update_webhook_url(
    request: ClientUpdateWebhookRequest,
    client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Update webhook URL for current client"""
    
    try:
        client.webhook_url = str(request.webhook_url)
        db.commit()
        db.refresh(client)
        
        logger.info(f"Client {client.email} updated webhook URL to {request.webhook_url}")
        
        return APIResponse(
            success=True,
            data={
                "webhook_url": client.webhook_url,
                "updated_at": client.updated_at.isoformat() if client.updated_at else None
            },
            message="Webhook URL updated successfully"
        )
    
    except Exception as e:
        logger.error(f"Error updating webhook URL: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Could not update webhook URL"
            }
        )


@router.put("/update-webhook", response_model=APIResponse)
async def update_webhook_with_apikey(
    request: ClientUpdateWebhookRequest,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """Update webhook URL using API Key (no login required)"""
    
    try:
        # Find client by API key
        client = db.query(Client).filter(Client.api_key == x_api_key).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_API_KEY",
                    "message": "Invalid API Key"
                }
            )
        
        if client.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "CLIENT_SUSPENDED",
                    "message": "Account has been suspended"
                }
            )
        
        # Update webhook URL
        client.webhook_url = str(request.webhook_url)
        client.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(client)
        
        logger.info(f"Client {client.app_id} updated webhook URL to {request.webhook_url} (via API key)")
        
        return APIResponse(
            success=True,
            data={
                "webhook_url": client.webhook_url,
                "updated_at": client.updated_at.isoformat() if client.updated_at else None
            },
            message="Webhook URL updated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhook URL: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Could not update webhook URL"
            }
        )
