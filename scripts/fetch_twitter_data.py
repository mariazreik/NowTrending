import requests
import sys
import json
import os

# Extend sys path to access the database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import TWITTER_API_KEY, TWITTER_API_HOST 

# API URLs for Twitter Data
HASHTAGS_API_URL = "https://twitter135.p.rapidapi.com/v1.1/Hashflags/"
TRENDS_API_URL = "https://twitter135.p.rapidapi.com/v1.1/Trends/"
LOCATION_API_URL = "https://twitter135.p.rapidapi.com/v1.1/Locations/"

# Request Headers with API credentials
HEADERS = {
    "x-rapidapi-key": TWITTER_API_KEY,
    "x-rapidapi-host": TWITTER_API_HOST
}


def make_api_request(url: str, params: dict = None) -> dict:
    """
    A helper function to make API requests and handle common errors.
    Args:
        url (str): The API endpoint URL.
        params (dict): The query parameters for the request.
    Returns:
        dict: JSON response from the API or None in case of error.
    """
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()  # Return the JSON data if successful
        else:
            # Handle non-200 status codes
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        # Catch all exceptions related to the request
        print(f"An error occurred while making the request: {e}")
        return None


def fetch_twitter_locations() -> dict:
    """
    Fetch locations from the Twitter API to get location IDs.
    Returns:
        dict: A dictionary containing location details.
    """
    return make_api_request(LOCATION_API_URL)


def fetch_twitter_hashtags() -> dict:
    """
    Fetch hashtags from the Twitter API.
    Returns:
        dict: A dictionary containing hashtags and their details.
    """
    return make_api_request(HASHTAGS_API_URL)


def fetch_twitter_trends(location_id: str) -> dict:
    """
    Fetch trending topics from the Twitter API for a specific location.
    Args:
        location_id (str): The ID of the location (e.g., a country or city).
    Returns:
        dict: A dictionary containing trending topics and their details.
    """
    url = TRENDS_API_URL
    params = {"location_id": location_id, "count": "20"}
    return make_api_request(url, params=params)


if __name__ == "__main__":
    # Fetch locations (to get location ID)
    location_id = -7608764736147602991
    locations = fetch_twitter_locations()
    if locations:
        print("Fetched Locations Data:")
        print(json.dumps(locations, indent=2, ensure_ascii=False))

        # Extract the location_id from the first entry
        if isinstance(locations, list) and len(locations) > 0:
            location_id = locations[0].get('place_id')  # Ensure correct key
            if location_id:
                print(f"Using location ID: {location_id}")
                # Fetch trends for the selected location
                trends = fetch_twitter_trends(location_id)
                if trends:
                    print("\nFetched Trending Data:")
                    print(json.dumps(trends, indent=2, ensure_ascii=False))
            else:
                print("Location ID not found in the response.")
        else:
            print("No locations found in the response.")
    else:
        print("Failed to fetch locations.")

    # Fetch hashtags
    hashtags = fetch_twitter_hashtags()
    if hashtags:
        print("Fetched Hashtags Data:")
        print(json.dumps(hashtags, indent=2, ensure_ascii=False))
    else:
        print("Failed to fetch hashtags.")
