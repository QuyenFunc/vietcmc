from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Index, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Admin(Base):
    """Admin model for storing admin users"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='admin', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_admins_email', 'email'),
    )


class Client(Base):
    """Client model for storing registered clients"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String(64), unique=True, nullable=False, index=True)
    organization_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    api_key = Column(String(128), unique=True, nullable=False, index=True)
    hmac_secret = Column(String(128), nullable=False)
    webhook_url = Column(Text, nullable=False)
    password_hash = Column(String(255), nullable=True)
    status = Column(String(20), default='active', nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_clients_status', 'status'),
        Index('idx_clients_created_at', 'created_at'),
    )


class Job(Base):
    """Job model for storing moderation jobs"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(64), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    comment_id = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    job_metadata = Column(JSON, nullable=True)
    
    # Processing info
    status = Column(String(20), default='queued', nullable=False, index=True)
    
    # Results
    sentiment = Column(String(20), nullable=True)
    moderation_result = Column(String(20), nullable=True, index=True)
    confidence_score = Column(Numeric(5, 4), nullable=True)
    reasoning = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Performance metrics
    processing_duration_ms = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index('idx_jobs_client_id', 'client_id'),
        Index('idx_jobs_status', 'status'),
        Index('idx_jobs_created_at', 'created_at'),
        Index('idx_jobs_moderation_result', 'moderation_result'),
        Index('idx_jobs_client_status_created', 'client_id', 'status', 'created_at'),
    )


class WebhookLog(Base):
    """Webhook log model for tracking webhook deliveries"""
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(64), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    webhook_url = Column(Text, nullable=False)
    
    # Request info
    request_payload = Column(JSON, nullable=False)
    request_headers = Column(JSON, nullable=True)
    
    # Response info
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Retry info
    attempt_number = Column(Integer, default=1, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_webhook_logs_job_id', 'job_id'),
        Index('idx_webhook_logs_client_id', 'client_id'),
        Index('idx_webhook_logs_status', 'status'),
        Index('idx_webhook_logs_sent_at', 'sent_at'),
    )

