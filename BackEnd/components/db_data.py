from pydantic import BaseModel
from components.plan_data import TravelPlan
from datetime import datetime

class DB_TravelPlan(BaseModel):
    user_id:str
    gen_time:datetime
    title:str
    travel_plan:TravelPlan
    # to find same plan
    location:str
    startDate:str
    endDate:str
    plan_id:str=None
    tag:str=None