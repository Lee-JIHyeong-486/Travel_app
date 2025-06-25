from pydantic import BaseModel
from typing import Optional, List, Any, Dict

# Pydantic models for validation (user_data defined)
class Duration(BaseModel):
    start: str
    end: str

class Kwargs(BaseModel):
    filter: Optional[List[Dict]] = None
    prev_map_data: Optional[Any] = None
    cache_key: Optional[str] = None

class UserRequest(BaseModel):
    user_id: str
    location: str
    duration: Duration
    companions: int
    concept: str
    extra_request: str
    kwargs: Kwargs