import httpx
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

async def get_coordinates(place: str):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": place, "key": API_KEY}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        data = res.json()
        if data["status"] == "OK":
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        return None

async def get_directions(locations: list[tuple[float, float]]):
    if len(locations) < 2:
        return None

    origin = f"{locations[0][0]},{locations[0][1]}"
    destination = f"{locations[-1][0]},{locations[-1][1]}"
    waypoints = "|".join(f"{lat},{lng}" for lat, lng in locations[1:-1]) if len(locations) > 2 else None

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "walking",
        "key": API_KEY
    }
    if waypoints:
        params["waypoints"] = f"optimize:true|{waypoints}"

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        return res.json()