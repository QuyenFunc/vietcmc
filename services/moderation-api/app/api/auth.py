from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt
import logging

from app.database import get_db
from app.config import settings
from app.models import Admin

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: str
    user: dict


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Admin login endpoint"""
    
    # Query admin user
    admin = db.query(Admin).filter(Admin.email == credentials.email).first()
    
    if not admin:
        logger.warning(f"Login attempt with unknown email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password (simple comparison for now, should use bcrypt in production)
    if admin.password_hash != credentials.password:
        logger.warning(f"Failed login attempt for admin: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if admin is active
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    admin.last_login_at = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": admin.email, "admin_id": admin.id}
    )
    
    logger.info(f"Successful login for admin: {credentials.email}")
    
    return LoginResponse(
        success=True,
        token=access_token,
        user={
            "id": admin.id,
            "email": admin.email,
            "name": admin.name,
            "role": admin.role
        }
    )


@router.post("/admin/logout")
async def admin_logout():
    """Admin logout endpoint"""
    return {"success": True, "message": "Logged out successfully"}

