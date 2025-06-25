from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
import time

class CacheData(BaseModel):
    data: Dict[str,Any]
    expires_at: float = Field(default_factory=lambda: time.time() + 3600)

    def update(self, value: dict):
        for key, val in value.items():
            self.data[key] = val

    def pop(self, key: str) -> Optional[dict]:
        value = self.data.pop(key, None)
        if value is not None:
            return {key: value}
        return None