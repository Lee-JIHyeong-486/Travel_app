from config import FOURSQUARE_API_KEY
from typing import List, Optional, Dict
import requests
from components.user_request_data import UserRequest
from components.poi_data import Place, Geometry
from datetime import datetime, timedelta
from modules.common.llm_request import request_to_llm
import json

FOURSQUARE_API_URL = "https://api.foursquare.com/v3/places/search"

HEADERS = {
    "Authorization": FOURSQUARE_API_KEY,
    "Accept": "application/json"
}

def get_fsq_id(name: str, lat: float, lng: float) -> str:
    HEADERS = { "Authorization":FOURSQUARE_API_KEY}
    
    params = {
        "query": name,
        "ll": f"{lat},{lng}",
        "limit": 1,
        "sort": "RELEVANCE"
    }
    response = requests.get(FOURSQUARE_API_URL, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    if results:
        return results[0].get("fsq_id")
    return None

def return_date_iter(start:str, end:str)->List[str]:
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    total_days = (end_date - start_date).days + 1
    date_list = [(start_date + timedelta(days=i)).isoformat() for i in range(total_days)]
    return date_list

def get_latlon_from_location(location: str) -> tuple[float, float]:
    geo_resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": location, "format": "json"},
        headers={'User-Agent': 'TravelPlannerApp/1.0 ehrms1009@hanmail.net'}
    )
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()
    return float(geo_data[0]["lat"]), float(geo_data[0]["lon"])

def get_base_from_llm(user_request:UserRequest, count=25) -> List[Place]:
    lat,lng = get_latlon_from_location(user_request.location)
    query = f"""
You are a travel planner assistant. Given the user's travel preferences and location, suggest {count} popular and general-interest base places to visit. Each place should be a must-see or representative of the area.

User Preferences:
- Concept: {user_request.concept}
- Extra Request: {user_request.extra_request}
- Location: {user_request.location} (lat: {lat}, lng: {lng})

For each place, return the following fields as JSON list of dicts with keys:
- name
- place_id (just use a unique string or name-based id if unavailable)
- lat
- lng
- categories (list of string)
Other fields (vicinity, rating, etc.) can be skipped or left as null.

Example output:
[
  {{
    "name": "Shibuya Crossing",
    "place_id": "shibuya-crossing",
    "lat": 35.6595,
    "lng": 139.7005,
    "categories": ["Landmark", "Tourist Attraction"]
  }},
  ...
]
"""
    response = request_to_llm(query)
    print("this is from get_base from llm:\n",response)
    try:
        parsed = json.loads(response)
        return [Place(
            name=p["name"],
            place_id=get_fsq_id(p["name"],p["lat"],p["lng"]),
            geometry=Geometry(lat=p["lat"], lng=p["lng"]),
            categories=p["categories"]
        ) for p in parsed]
    except Exception as e:
        print("⚠️ Failed to parse LLM base POI output:", e)
        return []

def sub_pois_for(lat, lng, filter, limit) -> List[Place]:
    category_id = filter.get("id", "")
    query = filter.get("query", "")

    params = {
        "ll": f"{lat},{lng}",
        "categories": category_id,
        "query": query,
        "limit": limit,
        "radius": 10000,
        "sort": "RELEVANCE"
    }

    response = requests.get(FOURSQUARE_API_URL, headers=HEADERS, params=params)
    response.raise_for_status()

    results = response.json().get("results", [])
    pois = []
    for place in results:
        pois.append(Place(
            name=place.get("name"),
            geometry=Geometry(lat=place["geocodes"]["main"]["latitude"],lng=place["geocodes"]["main"]["longitude"]),
            categories=[cat["name"] for cat in place.get("categories", [])],
            place_id=place.get("fsq_id")
        ))
    return pois

def get_sub_from_api(base:Place, filters, limit) -> List[Place]:
    lat = base.geometry.lat
    lng = base.geometry.lng
    sub_pois = []
    seen_ids = set()

    for f in filters:
        pois = sub_pois_for(lat, lng, f, limit)
        for p in pois:
            if p.place_id not in seen_ids:
                seen_ids.add(p.place_id)
                sub_pois.append(p)
    return sub_pois

def extract_pois(user_request:UserRequest, filters:List[Dict[str,str]], limit=5)-> Dict: # return {"base":List[Place], "sub":List[Place]}
    dates = return_date_iter(user_request.duration.start, user_request.duration.end)
    # step 1: get base poi per day(2) from llm
    print("start extracting base...")
    bases = get_base_from_llm(user_request, count=len(dates)*2)
    subs = []
    seen_ids = set()

    for base in bases:
        # step 2: get sub pois that related to base
        sub_pois = get_sub_from_api(base, filters, limit) # limit: upper limit of pois for each filter
        for poi in sub_pois:
            if poi.place_id not in seen_ids:
                seen_ids.add(poi.place_id)
                subs.append(poi)

    return {"base":bases, "sub":subs}

#  def get_pois_from_map(user_request: Optional[UserRequest] = None, filter_data: Optional[Dict[str,str]] = None, limit: int=50) -> List[dict]:
#     """
#     Fetches POIs using Foursquare Places API based on location and optional filter.
    
#     :param filter_data: Optional category keyword (e.g. "cafe", "museum")
#     :param location: Optional location string (e.g. "Seoul")
#     :return: List of POIs (each as a dictionary)
#     """
#     if not user_request.location:
#         raise ValueError("Location must be provided.")

#     # 1. convert location to corresponding to latitude/longitude
#     geo_resp = requests.get(
#         "https://nominatim.openstreetmap.org/search",
#         params={"q": user_request.location, "format": "json"},
#         headers={'User-Agent': 'TravelPlannerApp/1.0 ehrms1009@hanmail.net'}
#     )
#     # Check if the response is OK and contains JSON
#     if geo_resp.status_code == 200 and geo_resp.text.strip():
#         try:
#             geo_data = geo_resp.json()
#         except ValueError as e:
#             print("JSON decode error:", e)
#             print("Response content:", geo_resp.text)
#     else:
#         print(f"Request failed: status {geo_resp.status_code}")
#         print("Response content:", geo_resp.text)
    
#     lat = geo_data[0]["lat"]
#     lon = geo_data[0]["lon"]

#     # 2. request to foursquare api to get filter satisfying pois
#     params = {
#     "ll": f"{lat},{lon}",
#     "categories": filter_data or "",     # Category IDs like "10027,10028"
#     "query": user_request.concept,       # e.g., "art museum" or "family friendly"
#     "limit": limit,
#     "sort": "RELEVANCE",                 # Important: tells Foursquare to rank by query relevance
#     "radius":50000
#     }

#     response = requests.get(FOURSQUARE_API_URL, headers=HEADERS, params=params)
    
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch POIs: {response.text}")
    
#     results = response.json().get("results", [])
#     pois = []

#     # https://api.foursquare.com/v3/places/{fsq_id} => more detailed information about poi 
#     for place in results:
#         pois.append({
#             "name": place.get("name"),
#             "lat": place["geocodes"]["main"]["latitude"],
#             "lon": place["geocodes"]["main"]["longitude"],
#             "categories": [cat["name"] for cat in place.get("categories", [])],
#             "fsq_id": place.get("fsq_id")
#         })

#     return pois 