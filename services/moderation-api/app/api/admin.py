from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
import logging

from app.database import get_db
from app.models import Client, Job, WebhookLog, Admin
from app.schemas import APIResponse
from app.middleware.admin_auth import get_current_admin

logger = logging.getLogger(__name__)

router = APIRouter()


@router.delete("/admin/jobs/clear")
async def clear_all_jobs(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Clear all jobs from database (useful after load testing)"""
    try:
        deleted_count = db.query(Job).delete()
        db.commit()
        
        logger.info(f"Admin {admin.username} cleared {deleted_count} jobs")
        
        return APIResponse(
            success=True,
            data={
                "deleted_count": deleted_count,
                "message": f"Successfully deleted {deleted_count} jobs"
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing jobs: {e}")
        return APIResponse(
            success=False,
            error={
                "code": "DELETE_FAILED",
                "message": str(e)
            }
        )


@router.get("/admin/clients")
async def get_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get list of clients with pagination"""
    
    query = db.query(Client)
    
    if status:
        query = query.filter(Client.status == status)
    
    total = query.count()
    
    clients = query.order_by(desc(Client.created_at))\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()
    
    return APIResponse(
        success=True,
        data={
            "clients": [
                {
                    "id": c.id,
                    "app_id": c.app_id,
                    "organization_name": c.organization_name,
                    "email": c.email,
                    "webhook_url": c.webhook_url,
                    "status": c.status,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "last_used_at": c.last_used_at.isoformat() if c.last_used_at else None
                }
                for c in clients
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    )


@router.get("/admin/jobs")
async def get_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get list of jobs with pagination and filters"""
    
    query = db.query(Job)
    
    if status:
        query = query.filter(Job.status == status)
    
    if client_id:
        query = query.filter(Job.client_id == client_id)
    
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
                    "client_id": j.client_id,
                    "comment_id": j.comment_id,
                    "text": j.text[:100] + "..." if len(j.text) > 100 else j.text,
                    "status": j.status,
                    "sentiment": j.sentiment,
                    "moderation_result": j.moderation_result,
                    "confidence_score": float(j.confidence_score) if j.confidence_score else None,
                    "created_at": j.created_at.isoformat() if j.created_at else None,
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


@router.get("/admin/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get webhook logs"""
    
    query = db.query(WebhookLog)
    
    if status:
        query = query.filter(WebhookLog.status == status)
    
    total = query.count()
    
    logs = query.order_by(desc(WebhookLog.sent_at))\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()
    
    return APIResponse(
        success=True,
        data={
            "logs": [
                {
                    "id": l.id,
                    "job_id": l.job_id,
                    "client_id": l.client_id,
                    "webhook_url": l.webhook_url,
                    "status": l.status,
                    "response_status_code": l.response_status_code,
                    "response_time_ms": l.response_time_ms,
                    "attempt_number": l.attempt_number,
                    "error_message": l.error_message,
                    "sent_at": l.sent_at.isoformat() if l.sent_at else None
                }
                for l in logs
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    )


@router.get("/admin/stats")
async def get_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get dashboard statistics"""
    
    # Count jobs today
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    jobs_today = db.query(Job).filter(
        func.date(Job.created_at) == today
    ).count()
    
    # Count active clients
    active_clients = db.query(Client).filter(Client.status == 'active').count()
    
    # Calculate success rate
    total_jobs = db.query(Job).filter(Job.status == 'completed').count()
    failed_jobs = db.query(Job).filter(Job.status == 'failed').count()
    
    if total_jobs + failed_jobs > 0:
        success_rate = (total_jobs / (total_jobs + failed_jobs)) * 100
    else:
        success_rate = 0
    
    # Moderation results distribution
    allowed = db.query(Job).filter(Job.moderation_result == 'allowed').count()
    review = db.query(Job).filter(Job.moderation_result == 'review').count()
    reject = db.query(Job).filter(Job.moderation_result == 'reject').count()
    
    return APIResponse(
        success=True,
        data={
            "jobs_today": jobs_today,
            "active_clients": active_clients,
            "success_rate": round(success_rate, 2),
            "moderation_distribution": {
                "allowed": allowed,
                "review": review,
                "reject": reject
            }
        }
    )

