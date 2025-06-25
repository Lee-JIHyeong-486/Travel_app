# This page is getting actual route data from Open route service api
# backend/routes/ors_proxy.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from config import OPENROUTESERVICE_API_KEY

router = APIRouter()

class CoordinatesRequest(BaseModel):
    coordinates: list[list[float]]  # list of [lon, lat]

@router.post("/ors_proxy")
async def get_route(data: CoordinatesRequest):
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        "Authorization": OPENROUTESERVICE_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data.model_dump(), headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"ORS API request failed: {str(e)}")
