from pydantic import BaseModel
from typing import List, Optional

class Geometry(BaseModel):
    lat:float
    lng:float

class OpeningHours(BaseModel):
    open_now:bool

class Photos(BaseModel):
    photo_reference:str
    width:int
    height:int
    html_attributions:List[str]

class Place(BaseModel):
    name:str
    place_id:Optional[str]=None
    vicinity:Optional[str]=None
    geometry:Geometry
    categories:List[str]
    rating:Optional[float]=None
    user_ratings_total:Optional[int]=None
    opening_hours:Optional[OpeningHours] = None
    photos:Optional[Photos]=None
    icon:Optional[str]=None