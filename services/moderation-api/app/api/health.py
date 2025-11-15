from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import logging

from app.database import get_db
from app.schemas import HealthResponse, APIResponse
from app.config import settings
from app.utils.rabbitmq import rabbitmq_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    
    services_status = {}
    overall_status = "healthy"
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        services_status["database"] = "up"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services_status["database"] = "down"
        overall_status = "degraded"
    
    # Check RabbitMQ
    try:
        if rabbitmq_client.connection and not rabbitmq_client.connection.is_closed:
            services_status["message_broker"] = "up"
        else:
            services_status["message_broker"] = "down"
            overall_status = "degraded"
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        services_status["message_broker"] = "down"
        overall_status = "degraded"
    
    # Worker status (placeholder - would need actual worker monitoring)
    services_status["workers"] = {
        "active": 0,  # TODO: Get from monitoring
        "idle": 0
    }
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services_status,
        version=settings.APP_VERSION
    )

