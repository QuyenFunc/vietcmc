from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import logging

from app.database import get_db
from app.models import Admin
from app.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Middleware to authenticate admin requests using JWT token
    """
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        admin_id = payload.get("admin_id")
        
        if email is None or admin_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    # Query admin from database
    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.email == email).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is disabled"
        )
    
    return admin

