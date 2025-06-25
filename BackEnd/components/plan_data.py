from pydantic import BaseModel
from typing import List
from db.client import db  # MongoDB 연결 객체
from bson.objectid import ObjectId

class Location(BaseModel):
    latitude: float
    longitude: float

class Visiting(BaseModel):  # Capitalize class names by convention
    name: str
    location: Location
    concept: List[str]

class DayPlan(BaseModel):
    date: str
    place_to_visit: List[Visiting]  # List of Visiting objects

class TravelPlan(BaseModel):
    user_id: str
    plans: List[DayPlan]  # List of DayPlan objects

async def get_plan_by_id(plan_id: str):
    try:
        plan = await db.plans.find_one({"_id": ObjectId(plan_id)})
        if plan:
            plan["_id"] = str(plan["_id"])
        return plan
    except Exception as e:
        print(f"[🔥] DB 조회 중 예외 발생: {e}")
        return None

