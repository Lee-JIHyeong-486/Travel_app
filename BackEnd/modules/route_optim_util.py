from modules.common.llm_request import request_to_llm
from components.user_request_data import UserRequest
from components.llm_score_data import PlaceScore
from components.poi_data import Place, Geometry
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.common.poi_metadata import get_reviews
from modules.common.cache_util import load_data
import requests
import traceback

def get_scores_for_batch(batch: List[Dict], user_data: UserRequest) -> List[PlaceScore]: # batch: List[sub_pois+base]
    results: List[PlaceScore] = []
    print(f"this is batch:{type(batch)}")
    for place in batch:
        name = place.get("name")
        latitude = place.get("geometry").get("lat")
        longitude = place.get("geometry").get("lng")
        id = place.get("place_id")
        category = place.get("categories")

        # Step 1: Get reviews (black-box)
        reviews = get_reviews(name, id)  # Assume this returns a List[str] of review texts

        if not isinstance(reviews, list):
            print(f"⚠️ Invalid review data for {name}: {reviews}") # if there is no reviews or error in retrieving reviews, just ignore it

        # Step 2: Construct request for LLM
        try:
            reviews_text = "\n".join([f"{i+1}. {review['text']}" for i, review in enumerate(reviews)])
        except Exception as e:
            reviews_text = ""
            print(f"⚠️ Failed to format reviews for {name}: {e}, raw reviews: {reviews}")

        llm_prompt = f"""
You are a travel assistant helping a user select the most fitting places to visit.

The user’s preferences are as follows:
 - Companions: {user_data.companions}
 - Concepts: {user_data.concept}
 - Extra Requests: {user_data.extra_request}

You are given reviews for a place called "{name}".  
Read each review and evaluate **how well this place fits the user's preferences**, on a scale of 1 to 10 (10 = perfect match, 1 = very poor fit).

Respond with a **comma-separated list** of integers representing scores **in order** for each review (no text, no explanation, only numbers). Example: `7,6,8,5,...`
If there is no reviews, then just score it by yourself.
place categories:
{category}

Reviews:
{reviews_text}
"""

        # Step 3: Send to LLM
        response_text = request_to_llm(llm_prompt.strip())
        # Step 4: Parse scores
        try:
            score_strings = response_text.strip().split(",")
            scores = [int(s.strip()) for s in score_strings if s.strip().isdigit()]
        except Exception:
            scores = []

        if not scores:
            continue  # Skip if parsing failed

        # Step 5: Calculate average score
        avg_score = sum(scores) / len(scores)
        # Step 6: Create and add Place object
        results.append(PlaceScore(name=name, latitude=latitude, longitude=longitude, score=avg_score, category=category))
    print('batch result:\n', results)
    return results

def get_scores_from_llm(poi_list:Dict, user_data:UserRequest) -> Dict[str, List[PlaceScore]]: # poi_list: {"base", "sub"}
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i+chunk_size]
    bases = poi_list.get("base")
    print("this is from get scores from llm:\n",bases)
    subs = poi_list.get("sub")

    base_results:List[PlaceScore] = []
    sub_results:List[PlaceScore] = []
    chunk_size=5
    bases_batch = list(chunk_list(bases,chunk_size))
    sub_batch = list(chunk_list(subs, chunk_size))

    # 1. get scores for bases
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_scores_for_batch, batch, user_data) for batch in bases_batch]

        for future in futures:
            try:
                batch_result = future.result()
                base_results.extend(batch_result)
            except Exception as e:
                print("⚠️ Exception in future:")
                traceback.print_exc()
    # 2. get scores for subs
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_scores_for_batch, batch, user_data) for batch in sub_batch]

        for future in futures:
            try:
                sub_result = future.result()
                sub_results.extend(sub_result)
            except Exception as e:
                print("⚠️ Exception in future:")
                traceback.print_exc()
    return {"base":base_results,"sub":sub_results}

# ---- Helper to load pois ----
def load_pois(key):
    data = load_data(key)
    return data["poi_list"]

# def get_scores_for_batch(batch: List[Dict], user_data: UserRequest) -> List[PlaceScore]:
#     results: List[PlaceScore] = []

#     for place in batch:
#         name = place["name"]
#         latitude = place["lat"]
#         longitude = place["lon"]
#         id = place["fsq_id"]
#         category = place["categories"]

#         # Step 1: Get reviews (black-box)
#         reviews = get_reviews(name, id)  # Assume this returns a List[str] of review texts

#         if not isinstance(reviews, list):
#             print(f"⚠️ Invalid review data for {name}: {reviews}")
#             return []

#         # Step 2: Construct request for LLM
#         try:
#             reviews_text = "\n".join([f"{i+1}. {review['text']}" for i, review in enumerate(reviews)])
#         except Exception as e:
#             print(f"⚠️ Failed to format reviews for {name}: {e}, raw reviews: {reviews}")
#             return []

#         llm_prompt = f"""
# You are a travel assistant helping a user select the most fitting places to visit.

# The user’s preferences are as follows:
# - Companions: {user_data.companions}
# - Concepts: {user_data.concept}
# - Extra Requests: {user_data.extra_request}

# You are given reviews for a place called "{name}".  
# Read each review and evaluate **how well this place fits the user's preferences**, on a scale of 1 to 10 (10 = perfect match, 1 = very poor fit).

# Respond with a **comma-separated list** of integers representing scores **in order** for each review (no text, no explanation, only numbers). Example: `7,6,8,5,...`

# place categories:
# {category}

# Reviews:
# {reviews_text}
# """

#         # Step 3: Send to LLM
#         response_text = request_to_llm(llm_prompt.strip())
#         # Step 4: Parse scores
#         try:
#             score_strings = response_text.strip().split(",")
#             scores = [int(s.strip()) for s in score_strings if s.strip().isdigit()]
#         except Exception:
#             scores = []

#         if not scores:
#             continue  # Skip if parsing failed

#         # Step 5: Calculate average score
#         avg_score = sum(scores) / len(scores)
#         # Step 6: Create and add Place object
#         results.append(PlaceScore(name=name, latitude=latitude, longitude=longitude, score=avg_score, category=category))
#     print('batch result:\n', results)
#     return results

""" def get_scores_from_llm(poi_list:List[Dict], user_data:UserRequest):
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i+chunk_size]
    
    batch_size = 5
    batches = list(chunk_list(poi_list, batch_size))
    results = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_scores_for_batch, batch, user_data) for batch in batches]

        for future in futures:
            try:
                batch_result = future.result()
                results.extend(batch_result)
            except Exception as e:
                print("⚠️ Exception in future:")
                traceback.print_exc()
    return results """