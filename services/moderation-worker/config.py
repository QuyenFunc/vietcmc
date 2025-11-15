import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'vietcms_moderation')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'vietcms')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # RabbitMQ
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'password')
    
    @property
    def RABBITMQ_URL(self):
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
    
    # Worker settings
    WORKER_CONCURRENCY = int(os.getenv('WORKER_CONCURRENCY', 2))
    MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/phobert-base-v2')
    MODEL_DEVICE = os.getenv('MODEL_DEVICE', 'cpu')
    
    # Multi-task model settings
    USE_MULTITASK_MODEL = os.getenv('USE_MULTITASK_MODEL', 'true').lower() == 'true'
    # Increased threshold to reduce false positives - only block clearly toxic content
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.7))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


config = Config()

