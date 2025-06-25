from typing import List, Dict, Optional
import requests
import json
from config import FOURSQUARE_API_KEY

def get_reviews(name: str, fsq_id: str) -> Dict:
    """
    Get reviews for a given Foursquare place ID (fsq_id).
    
    Args:
        name (str): Name of the place (for reference/logging)
        fsq_id (str): Foursquare place ID
        
    Returns:
        Dict: Dictionary containing reviews data or error information
    """
    
    # Foursquare Places API endpoint for tips/reviews
    url = f"https://api.foursquare.com/v3/places/{fsq_id}/tips"
    
    # Headers for authentication
    headers = {
        "Authorization": FOURSQUARE_API_KEY,
        "Accept": "application/json"
    }
    
    # Parameters for the request
    params = {
        "limit": 50,  # Maximum number of reviews to fetch (max 50)
        "sort": "POPULAR"  # Sort by popularity, can also be "NEWEST"
    }
    
    try:
        print(f"Fetching reviews for: {name} (ID: {fsq_id})")
        
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()

            # Parse the response
            reviews_data = {
                "place_name": name,
                "fsq_id": fsq_id,
                "total_reviews": len(data),
                "reviews": []
            }
            # Extract review information
            for tip in data:
                review = {
                    "id": tip["id"],
                    "text": tip["text"],
                    "created_at": tip["created_at"],
                }
                reviews_data["reviews"].append(review)
            
            print(f"Successfully fetched {reviews_data['total_reviews']} reviews for {name} (ID: {fsq_id})")
            return reviews_data["reviews"]
            
        elif response.status_code == 401:
            error_msg = "Authentication failed. Please check your API key."
            print(f"Error: {error_msg}")
            return {"error": error_msg, "status_code": 401}
            
        elif response.status_code == 404:
            error_msg = f"Place not found for ID: {fsq_id}"
            print(f"Error: {error_msg}")
            return {"error": error_msg, "status_code": 404}
            
        elif response.status_code == 429:
            error_msg = "Rate limit exceeded. Please wait before making more requests."
            print(f"Error: {error_msg}")
            return {"error": error_msg, "status_code": 429}
            
        else:
            error_msg = f"API request failed with status code: {response.status_code}"
            print(f"Error: {error_msg}")
            print(f"Response: {response.text}")
            return {"error": error_msg, "status_code": response.status_code}
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        print(f"Error: {error_msg}")
        return {"error": error_msg}
    
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON response: {str(e)}"
        print(f"Error: {error_msg}")
        return {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Error: {error_msg}")
        return {"error": error_msg}

def get_poi_metadata(fsq_id:str) -> dict:
    url = f"https://api.foursquare.com/v3/places/{fsq_id}"
    
    headers = {
    "Authorization": FOURSQUARE_API_KEY,
    "Accept": "application/json"
    }

    metadata = requests.get(url, headers=headers)
    photos = requests.get(url+"/photos", headers=headers)
    photos_url = [f"{p['prefix']}original{p['suffix']}" for p in photos]

    return {"metadata":metadata, "photos":photos_url}