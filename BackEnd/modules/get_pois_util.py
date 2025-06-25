from modules.common.llm_request import request_to_llm
import json
from modules.common.cache_util import save_data
from typing import List, Dict
from components.user_request_data import UserRequest

def get_filter_from_llm(user_data:UserRequest) -> List[Dict[str, str]]:
    with open("public\concept_categories.json","r",encoding="utf-8") as file:
        whole_cat = json.load(file)
    category_group = whole_cat.get(user_data.concept)
    
    category_list = "\n".join(f"{k} ({v})" for k, v in category_group.items())

    prompt = f"""
You are a helpful travel planner assistant.

User profile:
- Companions: {user_data.companions}
- Travel theme: {user_data.concept}
- Extra request: {user_data.extra_request}

Below is a list of nature-related travel categories with their IDs:

{category_list}

For each category, decide if it fits the user's request and companions. 
If it fits, return a JSON object like:
{{"id": <category_id>, "query": "<search phrase>"}}

You may return **multiple categories** if several fit(3-4 is recommanded). Return a JSON list of these objects.
Do not include categories that don’t fit.
"""

    # Call LLM (adjust this part to your stack)
    response = request_to_llm(prompt)
    try:
        parsed = json.loads(response)  # parsed is now List[Dict[str, str]]
        return parsed
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        return []

# ---- Helper to save pois ----
# ---- save poi_list in cache ----
def save_pois(poi_list):
    payload = {
        "poi_list": poi_list
    }
    key = save_data(payload=payload)
    return key


""" def parse_filter_from_response(target_category, user_profile) -> List[dict]:
    if not target_category:
        return []
    instruction = (
    "You must select **ONLY FROM THE CATEGORIES LISTED BELOW**. Choose at most 3 categories that match the user's profile. "
    "Respond only in this format: {\"category\": [\"A\", \"B\"]} — the category names must match exactly from the list below.\n"
    "If none are suitable, return an empty list like this: {\"category\": []}.\n"
    "DO NOT invent new categories or rephrase them. Use copy-paste from the list.\n\n"
    f"CATEGORIES:\n{' / '.join(target_category)}\n\n"
    f"User Profile:\n{user_profile}"
    )

    response = request_to_llm(instruction)
    result = json.loads(response)
    chosens = result.get("category")
    return [{"chosen":chosen, "target_category":target_category} for chosen in chosens]

# Choose a Foursquare filter using LLM based on user preferences.
def get_filter_from_llm(user_data: UserRequest) -> List[str]:
    # Construct readable user profile
    user_profile = (
        f"Companions: {user_data.companions}.\n"
        f"Travel concept or theme: {user_data.concept}.\n"
        f"Additional requests: {user_data.extra_request}\n"
    )

    # Load category tree from JSON
    with open('public/category_tree.json', 'r', encoding='utf-8') as file:
        whole_category = json.load(file)
    target_category = whole_category["Category"]

    # Load id map from JSON
    with open('public/id_map.json', 'r', encoding='utf-8') as file:
        name_to_id = json.load(file)

    result_filters = []
    queue = deque([])

    chosens = parse_filter_from_response(target_category, user_profile)
    queue.extend(chosens)
    
    while True:
        if not queue:
            break
        try:
            # append filter in BFS style
            chosen_target = queue.popleft()
            chosen = chosen_target.get("chosen")
            target_category = chosen_target.get("target_category", [])

            if not chosen or chosen not in target_category:
                print(f"⚠️ Skipping invalid chosen category: '{chosen}'")
                continue  # Skip this iteration and go to next in queue

            category_id = name_to_id.get(chosen)
            if not category_id:
                print(f"⚠️ Category '{chosen}' not found in id mapping.")
                continue  # Skip if ID not found

            print(f"appending {category_id}... queue:{result_filters}")
            result_filters.append(category_id)

            # Proceed deeper in hierarchy
            target_category = whole_category.get(chosen, [])
            chosens = parse_filter_from_response(target_category, user_profile)
            queue.extend(chosens)

        except Exception as e:
            print(f"⚠️ Error during BFS filter parsing: {e}")
            continue
    return list(reversed(result_filters)) """

