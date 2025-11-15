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
    
    # Webhook settings
    WEBHOOK_TIMEOUT = int(os.getenv('WEBHOOK_TIMEOUT', 10))
    WEBHOOK_MAX_RETRIES = int(os.getenv('WEBHOOK_MAX_RETRIES', 3))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


config = Config()

