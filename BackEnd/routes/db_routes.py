
from fastapi import APIRouter, HTTPException
from fastapi.logger import logger
from datetime import datetime, timezone
from db.client import plans_collection
from components.db_data import DB_TravelPlan
from components.plan_data import TravelPlan
from components.user_request_data import UserRequest
from bson import ObjectId

router = APIRouter()

@router.post("/save_plan")
async def save_plan_in_db(user_req:UserRequest, travel_plan:TravelPlan):
    time = datetime.now(timezone.utc)
    # if there is same time duration and location plan, made a version of it
    # Build base title prefix for search
    base_title = f"travel to {user_req.location}({user_req.duration.start} ~ {user_req.duration.end})"

    # Find previous versions (title starts with base_title)
    prev_versions_cursor = plans_collection.find({
        "user_id": user_req.user_id,
        "startDate":user_req.duration.start,
        "endDate":user_req.duration.end
    })
    prev_versions = await prev_versions_cursor.to_list(length=None)

    # Determine new version number
    version_number = len(prev_versions) + 1

    # Final title
    title = f"{base_title} ver{version_number}"
    
    tp = DB_TravelPlan(
        user_id=user_req.user_id,
        gen_time=time, 
        title=title,
        travel_plan=travel_plan,
        location=user_req.location,
        startDate=user_req.duration.start,
        endDate=user_req.duration.end
        )
    await plans_collection.insert_one(tp.model_dump())
    return {"success":True}

# ---- Helper function for get_user_plans: convert user_ib object to str
def convert_objectid(doc):
    if isinstance(doc, list):
        return [convert_objectid(d) for d in doc]
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/load_plans")
async def get_user_plans(user_id: str):
    plans = await plans_collection.find({"user_id": user_id}).to_list(length=None)
    clean_plans= convert_objectid(plans)
    return {"value": clean_plans}

@router.delete("/delete_plan")
async def del_user_plan(_id:str):
    try:
        obj_id = ObjectId(_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid _id")

    result = await plans_collection.delete_one({"_id": obj_id})
    logger.info(f"Delete result for {_id}: {result.deleted_count}")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {"success": True}