from fastapi import APIRouter, HTTPException
from components.user_request_data import UserRequest
from modules.common.route_optimizer import optimize_route
from modules.route_optim_util import load_pois, get_scores_from_llm

router = APIRouter()

# ---- Main API Endpoint ----
@router.post("/route_optim")
def route_optim(user_request: UserRequest):
    try:
        # 1. Load POIs from CSV (or later redis)
        poi_list = load_pois(user_request.kwargs.cache_key)
    except Exception as e:
        print("error in loading pois")
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        # 2. Get scores from LLM
        scored_pois = get_scores_from_llm(poi_list, user_request)
        print('pois score:\n',scored_pois)
    except Exception as e:
        print("error in scoring pois")
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        # 3. Optimize route
        # travel_plan follows form of plan_data.TravelPlan
        travel_plan = optimize_route(user_request.user_id, user_request.duration, scored_pois)
        print('travel plan:\n', travel_plan)
        
        # 4. Return updated user_data + travel plan
        user_request.kwargs.prev_map_data = travel_plan

        # 5. Get recommanding accomodations
        accomodations = None
        
        return {
            "user_request": user_request,
            "travel_plan": travel_plan
        }
    
    except Exception as e:
        print("error in scheduling trip")
        raise HTTPException(status_code=500, detail=str(e))