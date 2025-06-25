from fastapi import APIRouter, Request
from modules.geo_utils import get_coordinates, get_directions

router = APIRouter()

@router.post("/get_coordinates")
async def coordinates_api(request: Request):
    data = await request.json()
    place = data.get("place")
    if not place:
        return {"error": "Missing place"}
    
    latlng = await get_coordinates(place)
    return {"coordinates": latlng}


@router.post("/get_directions")
async def directions_api(request: Request):
    data = await request.json()
    locations = data.get("locations")  # Expecting [[lat, lng], [lat, lng], ...]
    if not locations or len(locations) < 2:
        return {"error": "At least two locations are required"}
    
    directions = await get_directions(locations)
    return directions