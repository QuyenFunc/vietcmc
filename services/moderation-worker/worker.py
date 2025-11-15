import asyncio
import aio_pika
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys

from config import config

# Try to use new multi-task model, fallback to old inference
try:
    from nlp.inference_multitask import MultiTaskModerationInference
    USE_MULTITASK = True
    logger_temp = logging.getLogger(__name__)
except ImportError:
    from nlp.inference import ModerationInference
    USE_MULTITASK = False
    logger_temp = logging.getLogger(__name__)

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Load NLP model
if USE_MULTITASK and config.USE_MULTITASK_MODEL:
    logger.info("Loading Multi-Task PhoBERT model...")
    inference_model = MultiTaskModerationInference(
        model_path=config.MODEL_PATH,
        device=config.MODEL_DEVICE,
        confidence_threshold=config.CONFIDENCE_THRESHOLD
    )
    logger.info(f"Multi-Task model loaded from {config.MODEL_PATH}")
else:
    logger.info("Loading baseline inference model...")
    inference_model = ModerationInference(
        model_path=config.MODEL_PATH,
        device=config.MODEL_DEVICE
    )
    logger.info("Baseline model loaded")


async def process_job(message: aio_pika.IncomingMessage):
    """Process a moderation job"""
    async with message.process():
        try:
            # Parse message
            job_data = json.loads(message.body.decode('utf-8'))
            job_id = job_data['job_id']
            comment_text = job_data['text']
            
            logger.info(f"Processing job {job_id}")
            
            # Update job status to processing
            db = SessionLocal()
            try:
                from sqlalchemy import text as sql_text
                
                start_time = datetime.utcnow()
                
                db.execute(sql_text(
                    "UPDATE jobs SET status = 'processing', started_at = :started_at WHERE job_id = :job_id"
                ), {"started_at": start_time, "job_id": job_id})
                db.commit()
                
                # Run inference
                result = inference_model.predict(comment_text)
                
                # Calculate processing duration
                end_time = datetime.utcnow()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Extract results (compatible with both old and new format)
                if 'action' in result:
                    # New multi-task format
                    sentiment = 'negative' if result['action'] in ['review', 'reject'] else 'positive'
                    moderation_result = result['action']
                    confidence = result['confidence']
                    reasoning = result['reasoning']
                    
                    # Add extra metadata if available
                    if 'labels' in result and result['labels']:
                        reasoning += f" | Labels: {', '.join(result['labels'])}"
                else:
                    # Old format (backward compatible)
                    sentiment = result['sentiment']
                    moderation_result = result['moderation_result']
                    confidence = result['confidence']
                    reasoning = result['reasoning']
                
                # Update job with results
                db.execute(sql_text("""
                    UPDATE jobs 
                    SET status = 'completed',
                        sentiment = :sentiment,
                        moderation_result = :moderation_result,
                        confidence_score = :confidence_score,
                        reasoning = :reasoning,
                        completed_at = :completed_at,
                        processing_duration_ms = :duration_ms
                    WHERE job_id = :job_id
                """), {
                    "sentiment": sentiment,
                    "moderation_result": moderation_result,
                    "confidence_score": confidence,
                    "reasoning": reasoning,
                    "completed_at": end_time,
                    "duration_ms": duration_ms,
                    "job_id": job_id
                })
                db.commit()
                
                logger.info(f"Job {job_id} completed: {moderation_result} (confidence: {confidence:.2%})")
                
                # Publish job completed event
                connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
                channel = await connection.channel()
                
                exchange = await channel.declare_exchange(
                    "moderation_exchange",
                    aio_pika.ExchangeType.DIRECT,
                    durable=True
                )
                
                # Prepare webhook data
                completed_data = {
                    "job_id": job_id,
                    "client_id": job_data['client_id'],
                    "comment_id": job_data.get('comment_id'),
                    "text": comment_text,
                    "sentiment": sentiment,
                    "moderation_result": moderation_result,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "processing_duration_ms": duration_ms,
                    "completed_at": end_time.isoformat()
                }
                
                # Add multi-task specific data if available
                if 'labels' in result:
                    completed_data['detected_labels'] = result['labels']
                if 'severity_score' in result:
                    completed_data['severity_score'] = result['severity_score']
                
                await exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(completed_data).encode('utf-8'),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    ),
                    routing_key="moderation.job.completed"
                )
                
                await connection.close()
                
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Error processing job: {e}", exc_info=True)
            
            # Update job status to failed
            try:
                from sqlalchemy import text as sql_text
                db = SessionLocal()
                db.execute(sql_text(
                    "UPDATE jobs SET status = 'failed', completed_at = :completed_at WHERE job_id = :job_id"
                ), {"completed_at": datetime.utcnow(), "job_id": job_data.get('job_id', 'unknown')})
                db.commit()
                db.close()
            except:
                pass


async def main():
    """Main worker loop"""
    logger.info("Starting moderation worker...")
    
    # Connect to RabbitMQ
    connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
    channel = await connection.channel()
    
    # Set prefetch count for concurrency
    await channel.set_qos(prefetch_count=config.WORKER_CONCURRENCY)
    
    # Declare exchange
    exchange = await channel.declare_exchange(
        "moderation_exchange",
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )
    
    # Declare queue
    queue = await channel.declare_queue("moderation_jobs", durable=True)
    
    # Bind queue to exchange with routing key
    await queue.bind(exchange, routing_key="moderation.job.new")
    
    logger.info(f"Worker ready. Listening on queue 'moderation_jobs' with concurrency={config.WORKER_CONCURRENCY}")
    
    # Start consuming
    await queue.consume(process_job)
    
    # Keep running
    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker crashed: {e}", exc_info=True)
        sys.exit(1)

