import aio_pika
import json
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """RabbitMQ client for publishing and consuming messages"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.exchange_name = "moderation_exchange"
        self.queues = {
            "moderation_jobs": "moderation.job.new",
            "job_completed": "moderation.job.completed"
        }
    
    async def connect(self):
        """Establish connection to RabbitMQ"""
        import asyncio
        
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Connecting to RabbitMQ (attempt {attempt}/{max_retries})...")
                
                self.connection = await aio_pika.connect_robust(
                    settings.RABBITMQ_URL,
                    timeout=10
                )
                self.channel = await self.connection.channel()
                
                # Declare exchange
                self.exchange = await self.channel.declare_exchange(
                    self.exchange_name,
                    aio_pika.ExchangeType.DIRECT,
                    durable=True
                )
                
                # Declare queues
                for queue_name, routing_key in self.queues.items():
                    queue = await self.channel.declare_queue(
                        queue_name,
                        durable=True
                    )
                    await queue.bind(self.exchange, routing_key)
                
                logger.info("Connected to RabbitMQ successfully")
                return
            
            except Exception as e:
                logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Unable to connect to RabbitMQ")
                    raise
    
    async def publish_job(self, job_data: Dict[str, Any]):
        """Publish a moderation job to the queue"""
        if not self.exchange:
            await self.connect()
        
        try:
            message_body = json.dumps(job_data, ensure_ascii=False)
            
            message = aio_pika.Message(
                body=message_body.encode('utf-8'),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type='application/json'
            )
            
            await self.exchange.publish(
                message,
                routing_key=self.queues["moderation_jobs"]
            )
            
            logger.info(f"Published job {job_data.get('job_id')} to queue")
        
        except Exception as e:
            logger.error(f"Failed to publish job: {e}")
            raise
    
    async def publish_job_completed(self, job_data: Dict[str, Any]):
        """Publish job completion event"""
        if not self.exchange:
            await self.connect()
        
        try:
            message_body = json.dumps(job_data, ensure_ascii=False)
            
            message = aio_pika.Message(
                body=message_body.encode('utf-8'),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type='application/json'
            )
            
            await self.exchange.publish(
                message,
                routing_key=self.queues["job_completed"]
            )
            
            logger.info(f"Published job completed {job_data.get('job_id')}")
        
        except Exception as e:
            logger.error(f"Failed to publish job completed: {e}")
            raise
    
    async def close(self):
        """Close RabbitMQ connection"""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")


# Global instance
rabbitmq_client = RabbitMQClient()

