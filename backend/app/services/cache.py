import json
import redis.asyncio as redis
from typing import Dict, Any
import os

# Initialize Redis client using the environment variable or fallback to localhost
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

async def get_revenue_summary(property_id: str, tenant_id: str) -> Dict[str, Any]:
    """
    Fetches the revenue summary for a specific property.
    Uses a tenant-specific cache key to prevent cross-tenant data leaks.
    """
    # FIX: Added tenant_id to the cache key to isolate data per client
    cache_key = f"revenue:{tenant_id}:{property_id}"
    
    # Attempt to retrieve data from cache
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Calculate revenue via the reservation service if not cached
    from app.services.reservations import calculate_total_revenue
    
    result = await calculate_total_revenue(property_id, tenant_id)
    
    # Cache the newly calculated result for 5 minutes (300 seconds)
    await redis_client.setex(cache_key, 300, json.dumps(result))
    
    return result