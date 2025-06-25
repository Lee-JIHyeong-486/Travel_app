from fastapi import APIRouter, Body, HTTPException
from typing import Optional, Dict, Any
import time
from components.cache_data import CacheData

router = APIRouter()

# In-memory cache: { key: { value: any, expires_at: timestamp } }
cache = {}

# Save a data to in-memory cache with optional expiration
@router.post("/cache/save")
def cache_save(key: str, value: Dict = Body(...), expire: Optional[int] = None) -> None:
    expires_at = time.time() + expire if expire else time.time() + 3600
    value = value["value"]

    if key not in cache:
        cache[key] = CacheData(data=value,expires_at=expires_at)

    cache[key].update(value)

# Retrieve a data by key, checking expiration
@router.get("/cache/get")
def cache_get(key: str, extend_minutes: int = 30) -> Dict[str, Optional[Dict]]:
    item = cache.get(key)
    if not item:
        print("key not found")
        return {"value": None}  # Added return for consistency

    # Check expiration
    if item.expires_at and time.time() > item.expires_at:
        del cache[key]
        print("key expired")
        return {"value": None}  # Added return for consistency
    
    # Update expiration time to extend the cache lifetime
    if item.expires_at:  # Only update if there was an expiration time originally
        item.expires_at = time.time() + (extend_minutes * 60)
        print(f"Cache extended for key '{key}' by {extend_minutes} minutes")
    
    return {"value": item.data}


# Delete a data by key
@router.post("/cache/delete")
def cache_del(cache_key:str, data_key:str=None) -> Optional[Dict]:
    cache_data = cache.get(cache_key)

    if not cache_data:
        raise HTTPException(400, f"No such cache key: '{cache_key}'")

    if data_key is None:
        # Remove the entire CacheData entry
        removed = cache.pop(cache_key)
        return {
            "value": removed.data
        }
    
    result = cache_data.pop(data_key)
    if result:
        print(f"successfully remove {result} from {cache_key}")
        return {"value": result}
    else:
        raise HTTPException(status_code=404, detail=f"No such key '{data_key}' in cache '{cache_key}'")

# Check cache status
@router.get("/cache/status")
def cache_state(cache_key:str) -> Optional[Dict]:
    cache_data = cache.get(cache_key)
    if not cache_data:
        raise HTTPException(status_code=404, detail=f"No such key '{cache_key}' in cache'")
    return {"value":cache_data.data}