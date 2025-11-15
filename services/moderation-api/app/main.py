from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.utils.logging import setup_logging
from app.utils.rabbitmq import rabbitmq_client
from app.utils.redis_cache import redis_cache
from app.api import register, submit, status as status_api, health, admin, auth, client_auth
from app.middleware.rate_limit import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Connect to RabbitMQ
        await rabbitmq_client.connect()
        logger.info("RabbitMQ connection established")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
    
    try:
        # Connect to Redis
        redis_cache.connect()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await rabbitmq_client.close()
    redis_cache.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.API_CORS_ALLOW_METHODS,
    allow_headers=settings.API_CORS_ALLOW_HEADERS,
    expose_headers=["*"],
    max_age=settings.API_CORS_MAX_AGE,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred"
            }
        }
    )


# Setup Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(register.router, tags=["Registration"])  # Mount without prefix for direct access at /register
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(client_auth.router, prefix="/api/v1", tags=["Client Auth"])
app.include_router(submit.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(status_api.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])


# Root endpoint
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

