from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models import Job
from app.schemas import JobStatusResponse, APIResponse
from app.middleware.auth import get_current_client
from app.middleware.rate_limit import limiter
from app.utils.redis_cache import redis_cache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status/{job_id}", response_model=APIResponse)
@limiter.limit("10000/minute")  # Higher limit for status checks
async def get_job_status(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get status of a moderation job (with Redis caching for completed jobs)"""
    
    try:
        # Authenticate client
        client = await get_current_client(request, db=db)
        
        # Check cache for completed jobs
        cache_key = f"job_status:{client.id}:{job_id}"
        cached_result = redis_cache.get(cache_key)
        
        if cached_result and cached_result.get('status') == 'completed':
            logger.debug(f"Cache hit for job {job_id}")
            return APIResponse(
                success=True,
                data=cached_result
            )
        
        # Query job from database
        job = db.query(Job).filter(
            Job.job_id == job_id,
            Job.client_id == client.id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "JOB_NOT_FOUND",
                    "message": "Job not found or does not belong to this client"
                }
            )
        
        # Prepare response based on job status
        response_data = {
            "job_id": job.job_id,
            "status": job.status,
            "created_at": job.created_at
        }
        
        if job.status == 'completed':
            response_data.update({
                "comment_id": job.comment_id,
                "text": job.text,
                "result": {
                    "sentiment": job.sentiment,
                    "moderation_result": job.moderation_result,
                    "confidence": float(job.confidence_score) if job.confidence_score else None,
                    "reasoning": job.reasoning
                },
                "completed_at": job.completed_at,
                "processing_duration_ms": job.processing_duration_ms
            })
        elif job.status == 'processing':
            response_data["started_at"] = job.started_at
        elif job.status == 'queued':
            # Could add queue position here
            pass
        
        # Cache completed jobs for 1 hour to reduce DB load
        if job.status == 'completed':
            redis_cache.set(cache_key, response_data, ttl=3600)
        
        return APIResponse(
            success=True,
            data=response_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to get job status"
            }
        )

