from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "VietCMS Moderation API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "vietcms_moderation"
    POSTGRES_USER: str = "vietcms"
    POSTGRES_PASSWORD: str = "password"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # RabbitMQ
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "admin"
    RABBITMQ_PASS: str = "password"
    
    @property
    def RABBITMQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Security
    API_SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_SECRET_KEY: str = "change-this-jwt-secret-key-in-production"
    API_RATE_LIMIT: int = 1000
    
    # CORS
    API_CORS_ORIGINS: str = "*"  # In production, set specific origins
    API_CORS_ALLOW_METHODS: List[str] = ["*"]
    API_CORS_ALLOW_HEADERS: List[str] = ["*"]
    API_CORS_MAX_AGE: int = 600
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.API_CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.API_CORS_ORIGINS.split(",")]
    
    @property
    def CORS_ALLOW_CREDENTIALS(self) -> bool:
        # Cannot use credentials with wildcard origins
        return self.API_CORS_ORIGINS != "*"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

