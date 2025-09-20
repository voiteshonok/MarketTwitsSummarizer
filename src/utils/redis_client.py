"""Redis client for caching and data storage."""

import json
import pickle
from typing import Any, Optional, Union
import redis
from .config import config
from .logger import logger


class RedisClient:
    """Redis client wrapper for the MarketTwits Summarizer."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )
        self._test_connection()
    
    def _test_connection(self):
        """Test Redis connection."""
        try:
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)
            elif not isinstance(value, str):
                value = str(value)
            
            result = self.redis_client.set(key, value, ex=expire)
            logger.debug(f"Set key '{key}' in Redis")
            return result
        except Exception as e:
            logger.error(f"Failed to set key '{key}' in Redis: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Retrieved key '{key}' from Redis")
            return value
        except Exception as e:
            logger.error(f"Failed to get key '{key}' from Redis: {e}")
            return None
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get and parse JSON value from Redis."""
        try:
            value = self.get(key)
            if value:
                return json.loads(value)
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON for key '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            result = self.redis_client.delete(key)
            logger.debug(f"Deleted key '{key}' from Redis")
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete key '{key}' from Redis: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check existence of key '{key}' in Redis: {e}")
            return False
    
    def set_hash(self, name: str, mapping: dict) -> bool:
        """Set a hash in Redis."""
        try:
            result = self.redis_client.hset(name, mapping=mapping)
            logger.debug(f"Set hash '{name}' in Redis")
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set hash '{name}' in Redis: {e}")
            return False
    
    def get_hash(self, name: str) -> Optional[dict]:
        """Get a hash from Redis."""
        try:
            result = self.redis_client.hgetall(name)
            if result:
                logger.debug(f"Retrieved hash '{name}' from Redis")
            return result
        except Exception as e:
            logger.error(f"Failed to get hash '{name}' from Redis: {e}")
            return None
    
    def add_to_set(self, name: str, *values) -> int:
        """Add values to a set in Redis."""
        try:
            result = self.redis_client.sadd(name, *values)
            logger.debug(f"Added {result} values to set '{name}' in Redis")
            return result
        except Exception as e:
            logger.error(f"Failed to add values to set '{name}' in Redis: {e}")
            return 0
    
    def get_set_members(self, name: str) -> set:
        """Get all members of a set from Redis."""
        try:
            result = self.redis_client.smembers(name)
            logger.debug(f"Retrieved {len(result)} members from set '{name}' in Redis")
            return result
        except Exception as e:
            logger.error(f"Failed to get members from set '{name}' in Redis: {e}")
            return set()


# Global Redis client instance
redis_client = RedisClient()
