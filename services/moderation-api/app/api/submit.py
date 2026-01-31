from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import uuid

from app.database import get_db
from app.models import Client, Job
from app.schemas import JobSubmitRequest, JobSubmitResponse, APIResponse
from app.middleware.auth import get_current_client, verify_request_signature
from app.middleware.rate_limit import limiter
from app.utils.rabbitmq import rabbitmq_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/submit", response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10000/minute")  # Limit to 10000 requests per minute per IP/client
async def submit_job(
    request: Request,
    job_request: JobSubmitRequest,
    db: Session = Depends(get_db)
):
    """Submit a comment for moderation"""
    
    try:
        # Authenticate client
        client = await get_current_client(request, db=db)
        
        # Verify HMAC signature
        await verify_request_signature(request, client)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Store type in metadata for persistence without schema change
        metadata = job_request.metadata or {}
        if 'type' not in metadata:
            metadata['type'] = job_request.type

        # Create job record
        new_job = Job(
            job_id=job_id,
            client_id=client.id,
            comment_id=job_request.comment_id,
            text=job_request.text,
            job_metadata=metadata,
            status='queued'
        )
        
        db.add(new_job)
        db.commit()
        
        # Publish to RabbitMQ
        job_data = {
            "job_id": job_id,
            "client_id": client.id,
            "comment_id": job_request.comment_id,
            "text": job_request.text,
            "type": job_request.type,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await rabbitmq_client.publish_job(job_data)
        
        logger.info(f"Job {job_id} submitted by client {client.app_id}")
        
        # Update client last_used_at
        client.last_used_at = datetime.utcnow()
        db.commit()
        
        # Prepare response
        response_data = JobSubmitResponse(
            job_id=job_id,
            status='queued',
            created_at=new_job.created_at,
            estimated_processing_time_ms=2000
        )
        
        return APIResponse(
            success=True,
            data=response_data.dict(),
            message="Job accepted for processing"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting job: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Failed to submit job"
            }
        )

