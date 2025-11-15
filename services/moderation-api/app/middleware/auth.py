from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.models import Client
from app.utils.auth import verify_hmac_signature

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_client(
    request: Request,
    api_key: Optional[str] = None,
    db: Session = None
) -> Client:
    """Middleware to authenticate API requests"""
    
    if not api_key:
        api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_API_KEY",
                "message": "Invalid or missing API key"
            }
        )
    
    # Query client from database
    if db is None:
        db = next(get_db())
    
    client = db.query(Client).filter(Client.api_key == api_key).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_API_KEY",
                "message": "Invalid or missing API key"
            }
        )
    
    if client.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CLIENT_SUSPENDED",
                "message": "Client account is suspended"
            }
        )
    
    return client


async def verify_request_signature(
    request: Request,
    client: Client
) -> bool:
    """Verify HMAC signature of request"""
    
    signature = request.headers.get("X-Hub-Signature-256")
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INVALID_SIGNATURE",
                "message": "Missing HMAC signature"
            }
        )
    
    # Get request body
    body = await request.body()
    
    # Verify signature
    if not verify_hmac_signature(client.hmac_secret, body, signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "INVALID_SIGNATURE",
                "message": "HMAC signature verification failed"
            }
        )
    
    return True

