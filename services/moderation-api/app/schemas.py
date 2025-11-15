from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, Dict, Any
from datetime import datetime


# Request schemas
class ClientRegisterRequest(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    webhook_url: HttpUrl


class ClientLoginRequest(BaseModel):
    email: EmailStr
    password: str


class ClientUpdateWebhookRequest(BaseModel):
    webhook_url: HttpUrl


class JobSubmitRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    comment_id: Optional[str] = Field(None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None


# Response schemas
class ClientRegisterResponse(BaseModel):
    app_id: str
    api_key: str
    hmac_secret: str
    webhook_url: str
    created_at: datetime


class JobSubmitResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    estimated_processing_time_ms: int = 2000


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    comment_id: Optional[str] = None
    text: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_duration_ms: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, Any]
    version: str


# Generic response wrapper
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None


# Error response
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

