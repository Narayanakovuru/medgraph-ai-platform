import redis
from app.core.config import settings

# Initialize Redis client using configuration settings
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

def get_redis_client() -> redis.Redis:
    """Dependency helper to get the active Redis client."""
    return redis_client