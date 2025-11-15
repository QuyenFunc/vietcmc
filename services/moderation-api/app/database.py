from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine with optimized connection pool for high load
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=30,  # Base connection pool size (increased for high load)
    max_overflow=50,  # Additional connections when pool is full
    pool_timeout=30,  # Timeout waiting for connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Disable SQL logging in production
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

