import asyncio
import aio_pika
import aiohttp
import json
import logging
import hmac
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys

from config import config

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


def generate_hmac_signature(secret: str, body: bytes) -> str:
    """Generate HMAC-SHA256 signature for webhook"""
    signature = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return f"sha256={signature}"


async def send_webhook(
    webhook_url: str,
    hmac_secret: str,
    payload: dict,
    attempt: int = 1
) -> tuple[bool, int, str, int]:
    """
    Send webhook with HMAC signature
    
    Returns:
        (success, status_code, response_body, response_time_ms)
    """
    try:
        # Prepare payload
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        
        # Generate HMAC signature
        signature = generate_hmac_signature(hmac_secret, body)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': signature,
            'User-Agent': 'VietCMS-Moderation/1.0'
        }
        
        # Send request
        start_time = datetime.utcnow()
        
        timeout = aiohttp.ClientTimeout(total=config.WEBHOOK_TIMEOUT)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(webhook_url, data=body, headers=headers) as response:
                response_body = await response.text()
                status_code = response.status
                
                end_time = datetime.utcnow()
                response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                success = 200 <= status_code < 300
                
                return success, status_code, response_body[:1000], response_time_ms  # Limit response body size
    
    except asyncio.TimeoutError:
        logger.warning(f"Webhook timeout after {config.WEBHOOK_TIMEOUT}s (attempt {attempt})")
        return False, 0, f"Timeout after {config.WEBHOOK_TIMEOUT}s", config.WEBHOOK_TIMEOUT * 1000
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return False, 0, str(e)[:1000], 0


async def process_webhook(message: aio_pika.IncomingMessage):
    """Process webhook delivery with retry logic"""
    async with message.process():
        try:
            # Parse message
            job_data = json.loads(message.body.decode('utf-8'))
            job_id = job_data['job_id']
            client_id = job_data['client_id']
            
            logger.info(f"Processing webhook for job {job_id}")
            
            # Get client webhook URL and secret from database
            db = SessionLocal()
            try:
                result = db.execute(
                    text("SELECT webhook_url, hmac_secret FROM clients WHERE id = :client_id"),
                    {"client_id": client_id}
                ).fetchone()
                
                if not result:
                    logger.error(f"Client {client_id} not found")
                    return
                
                webhook_url, hmac_secret = result
                
                # Prepare webhook payload
                payload = {
                    "job_id": job_id,
                    "comment_id": job_data.get('comment_id'),
                    "text": job_data['text'],
                    "sentiment": job_data['sentiment'],
                    "moderation_result": job_data['moderation_result'],
                    "confidence": job_data['confidence'],
                    "reasoning": job_data.get('reasoning'),
                    "timestamp": job_data.get('completed_at', datetime.utcnow().isoformat())
                }
                
                # Attempt webhook delivery with retry
                for attempt in range(1, config.WEBHOOK_MAX_RETRIES + 1):
                    logger.info(f"Webhook attempt {attempt}/{config.WEBHOOK_MAX_RETRIES} for job {job_id}")
                    
                    success, status_code, response_body, response_time_ms = await send_webhook(
                        webhook_url,
                        hmac_secret,
                        payload,
                        attempt
                    )
                    
                    # Log webhook delivery
                    db.execute(text("""
                        INSERT INTO webhook_logs (
                            job_id, client_id, webhook_url, request_payload,
                            request_headers, response_status_code, response_body,
                            response_time_ms, attempt_number, status, error_message
                        ) VALUES (
                            :job_id, :client_id, :webhook_url, :request_payload,
                            :request_headers, :response_status_code, :response_body,
                            :response_time_ms, :attempt_number, :status, :error_message
                        )
                    """), {
                        "job_id": job_id,
                        "client_id": client_id,
                        "webhook_url": webhook_url,
                        "request_payload": json.dumps(payload),
                        "request_headers": json.dumps({"X-Hub-Signature-256": "***"}),
                        "response_status_code": status_code if status_code else None,
                        "response_body": response_body,
                        "response_time_ms": response_time_ms,
                        "attempt_number": attempt,
                        "status": "success" if success else ("retrying" if attempt < config.WEBHOOK_MAX_RETRIES else "failed"),
                        "error_message": response_body if not success else None
                    })
                    db.commit()
                    
                    if success:
                        logger.info(f"Webhook delivered successfully for job {job_id}")
                        break
                    
                    # Wait before retry (exponential backoff)
                    if attempt < config.WEBHOOK_MAX_RETRIES:
                        wait_time = 5 * (2 ** (attempt - 1))  # 5s, 10s, 20s
                        logger.info(f"Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Webhook failed after {config.WEBHOOK_MAX_RETRIES} attempts for job {job_id}")
            
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)


async def main():
    """Main dispatcher loop"""
    logger.info("Starting webhook dispatcher...")
    
    # Connect to RabbitMQ with retry
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connecting to RabbitMQ (attempt {attempt}/{max_retries})...")
            connection = await aio_pika.connect_robust(
                config.RABBITMQ_URL,
                timeout=10
            )
            logger.info("Successfully connected to RabbitMQ")
            break
        except Exception as e:
            logger.warning(f"Failed to connect to RabbitMQ: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Unable to connect to RabbitMQ")
                raise
    
    try:
        channel = await connection.channel()
        
        # Set prefetch count for high concurrency - process 50 webhooks in parallel
        await channel.set_qos(prefetch_count=50)
        
        # Declare queue
        queue = await channel.declare_queue("job_completed", durable=True)
        
        logger.info("Webhook dispatcher ready. Listening on queue 'job_completed'")
        
        # Start consuming
        await queue.consume(process_webhook)
        
        # Keep running
        await asyncio.Future()
    except asyncio.CancelledError:
        logger.info("Dispatcher cancelled")
        raise
    finally:
        logger.info("Closing RabbitMQ connection...")
        await connection.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Dispatcher stopped by user")
    except Exception as e:
        logger.error(f"Dispatcher crashed: {e}", exc_info=True)
        sys.exit(1)

