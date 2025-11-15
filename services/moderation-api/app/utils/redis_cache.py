import redis
import json
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache client for caching API responses and reducing database load"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.connected = False
    
    def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            # Test connection
            self.client.ping()
            self.connected = True
            logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
    
    def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            try:
                self.client.close()
                logger.info("Disconnected from Redis")
            except Exception as e:
                logger.error(f"Error disconnecting from Redis: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.connected:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Redis GET error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 5 minutes)
        """
        if not self.connected:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis SET error for key {key}: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.connected:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.connected:
            return False
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            logger.warning(f"Redis INVALIDATE error for pattern {pattern}: {e}")
            return False


# Global Redis cache instance
redis_cache = RedisCache()

