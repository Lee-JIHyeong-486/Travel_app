from typing import TypedDict, List

class PlaceScore(TypedDict):
    name: str
    latitude: float
    longitude: float
    score: float
    category: List[str]