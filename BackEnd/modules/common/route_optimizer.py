from components.plan_data import Location, Visiting, DayPlan, TravelPlan
from components.user_request_data import Duration
from components.llm_score_data import PlaceScore
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import requests
import numpy as np
# ---- remove after implementing naver api
import math
from sklearn.cluster import DBSCAN

# ---- optimize_helper ----
# return list of dates within duration.start and duration.end
def get_days(duration: Duration) -> List[str]:
    start_date = datetime.strptime(duration.start, "%Y-%m-%d")
    end_date = datetime.strptime(duration.end, "%Y-%m-%d")
    delta = end_date - start_date

    return [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(delta.days + 1)
    ]

def get_distance(start_lat, start_lng, end_lat, end_lng, mode="driving"):
    return math.sqrt((start_lat - end_lat)**2 + (start_lng - end_lng)**2)

def cluster_pois(pois: List[Visiting], eps=0.05, min_samples=2) -> List[int]:
    """
    Cluster POIs based on geographic proximity using DBSCAN
    
    Args:
        pois: List of Visiting objects
        eps: The maximum distance between two samples for them to be considered as in the same neighborhood
        min_samples: The number of samples in a neighborhood for a point to be considered as a core point
        
    Returns:
        List of cluster labels for each POI
    """
    if not pois:
        return []
        
    # Extract coordinates from POIs
    coordinates = np.array([[float(poi.location.latitude), float(poi.location.longitude)] for poi in pois])
    
    # Apply DBSCAN clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coordinates)
    
    # Return cluster labels
    return clustering.labels_.tolist()

def softmax(scores: List[float]) -> List[float]:
    """
    Apply softmax function to convert scores to probabilities
    
    Args:
        scores: List of scores
        
    Returns:
        List of probabilities
    """
    # Convert to numpy array and apply softmax
    exp_scores = np.exp(np.array(scores))
    return (exp_scores / exp_scores.sum()).tolist()

def next_visit(scores: List[float], pois: List[Visiting], clusters: Optional[List[int]], 
               prev_visit: Optional[Visiting] = None, prev_cluster: Optional[int]=None, incentive_factor: float = 1.3) -> Visiting:
    # Create a copy of scores to modify
    adjusted_scores = scores.copy()
    
    # Apply incentive for POIs in the same cluster as prev_visit
    if prev_cluster is not None and prev_cluster != -1:
        for i, cluster in enumerate(clusters):
            if cluster == prev_cluster:
                adjusted_scores[i] *= incentive_factor
    
    # Apply softmax to get probabilities
    probabilities = softmax(adjusted_scores)
    
    # Select the POI with the highest probability
    selected_idx = np.argmax(probabilities)
    selected_poi = pois[selected_idx]

    return selected_poi
def optimize_route(user_id: str, duration: Duration, pois_data: Dict[str, List[PlaceScore]], visits_per_day: int = 3, score_threshold=0) -> TravelPlan:
    days = get_days(duration)

    def parse_and_filter(pois: List[PlaceScore]):
        parsed_pois = []
        scores = []
        for poi_dict in pois:
            poi = Visiting(
                name=poi_dict['name'],
                location=Location(
                    latitude=poi_dict['latitude'],
                    longitude=poi_dict['longitude']
                ),
                concept=poi_dict['category']
            )
            parsed_pois.append(poi)
            scores.append(float(poi_dict['score']))
        filtered_indices = [i for i, s in enumerate(scores) if s >= score_threshold]
        return [parsed_pois[i] for i in filtered_indices], [scores[i] for i in filtered_indices]

    # Separate base and sub POIs
    base_pois, base_scores = parse_and_filter(pois_data.get("base", []))
    sub_pois, sub_scores = parse_and_filter(pois_data.get("sub", []))

    # Early return if either list is empty
    if not base_pois:
        return TravelPlan(user_id=user_id, plans=[])

    # Cluster sub POIs only (base has no cluster logic)
    sub_clusters = cluster_pois(sub_pois)

    travel_plan = TravelPlan(user_id=user_id, plans=[])

    for day_idx in range(len(days)):
        current_date = days[day_idx]
        day_plan = DayPlan(date=current_date, place_to_visit=[])

        if not base_pois:
            break  # no more base options to start the day

        # 1. First POI from base
        first_poi = next_visit(base_scores, base_pois, None, None, None)
        day_plan.place_to_visit.append(first_poi)
        idx = base_pois.index(first_poi)
        base_pois.pop(idx)
        base_scores.pop(idx)
        prev_visit = first_poi
        prev_cluster = None

        # 2. Follow-up visits from sub
        for _ in range(min(visits_per_day - 1, len(sub_pois))):
            if not sub_pois:
                break
            next_poi = next_visit(sub_scores, sub_pois, sub_clusters, prev_visit, prev_cluster)
            day_plan.place_to_visit.append(next_poi)
            idx = sub_pois.index(next_poi)
            sub_pois.pop(idx)
            sub_scores.pop(idx)
            prev_cluster = sub_clusters.pop(idx)
            prev_visit = next_poi

        travel_plan.plans.append(day_plan)

    return travel_plan

""" def optimize_route(user_id: str, duration: Duration, pois_data: Dict[str,List[PlaceScore]], visits_per_day: int = 3, score_threshold=7.4) -> TravelPlan:  
    days = get_days(duration)
    # Convert dictionary POIs to Visiting objects and extract scores
    pois = []
    scores = []
    
    for poi_dict in pois_data:
        # Convert dictionary to Visiting object
        poi = Visiting(
            name=poi_dict['name'],
            location=Location(
                latitude=poi_dict['latitude'],
                longitude=poi_dict['longitude']
            ),
            concept=poi_dict['category']
        )
        pois.append(poi)
        
        # Extract score (convert from string to float)
        scores.append(float(poi_dict['score']))

    # Filter POIs based on score threshold
    filtered_indices = [i for i, score in enumerate(scores) if score >= score_threshold]
    filtered_pois = [pois[i] for i in filtered_indices]
    filtered_scores = [scores[i] for i in filtered_indices]

    # Early return if no POIs meet the threshold
    if not filtered_pois:
        return TravelPlan(user_id=user_id, plans=[])
        
    # Cluster POIs (only the filtered ones)
    clusters = cluster_pois(filtered_pois)

    # Create a copy of POIs and scores to modify
    remaining_pois = filtered_pois.copy()
    remaining_scores = filtered_scores.copy()
    remaining_clusters = clusters.copy()

    # Initialize travel plan
    travel_plan = TravelPlan(user_id=user_id, plans=[])

    # Create day plans
    for day_idx in range(len(days)):
        current_date = days[day_idx]

        # Initialize day plan
        day_plan = DayPlan(date=current_date, place_to_visit=[])
        
        # Previous visit, initially None
        prev_visit = None
        prev_cluster = None
        
        # Add visits for the day
        for _ in range(min(visits_per_day, len(remaining_pois))):
            if not remaining_pois:
                break
                
            # Get next POI to visit
            next_poi = next_visit(
                remaining_scores, 
                remaining_pois, 
                remaining_clusters, 
                prev_visit,
                prev_cluster
            )
            
            # Add POI to day plan
            day_plan.place_to_visit.append(next_poi)
            
            # Update previous visit
            prev_visit = next_poi
            
            # Remove selected POI from remaining POIs and scores
            idx = remaining_pois.index(next_poi)
            remaining_pois.pop(idx)
            remaining_scores.pop(idx)
            prev_cluster = remaining_clusters.pop(idx)
        
        # Add day plan to travel plan
        travel_plan.plans.append(day_plan)
    
    return travel_plan """