from fastapi import APIRouter, HTTPException
from components.user_request_data import UserRequest
from modules.common.get_pois_from_map import extract_pois
from modules.get_pois_util import get_filter_from_llm, save_pois

router = APIRouter()

@router.post("/get_pois")
def get_pois(user_request: UserRequest):
    # ignore next step if it is feedback step
    if user_request.kwargs.cache_key:
        pass
    try:
        filter_data = user_request.kwargs.filter

        # Step 1: If no filter, call LLM to generate it
        if not filter_data:
            filter_data = get_filter_from_llm(user_request)
            user_request.kwargs.filter = filter_data
        print(f'filter(type:{type(filter_data)}):\n', filter_data)
    except Exception as e:
        print("filter creation failed")
        raise HTTPException(status_code=500, detail=str(e))
    try:
        # Step 2: Fetch POIs based on filter
        poi_list = extract_pois(user_request, filter_data, limit=3)
        print('poi list:\n',poi_list)
    except Exception as e:
        print("poi extraction failed")
        raise HTTPException(status_code=500, detail=str(e))
    try:
        # Step 3: Save to CSV
        user_request.kwargs.cache_key = save_pois(poi_list)
        print("finish saving pois")
        # Step 4: Return result
        return {
            "user_request": user_request.model_dump()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))