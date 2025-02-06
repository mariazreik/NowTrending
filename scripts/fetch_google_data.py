import os
import sys
import requests
import streamlit as st

# Extend sys path to access the database module or config in parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import GOOGLE_API_HOST, GOOGLE_API_KEY

GOOGLE_API_URL = "https://google-realtime-trends-data-api.p.rapidapi.com/trends"

# Google Trends API
GOOGLE_API_KEY=afst.secrets["GOOGLE_API_KEY"]["GOOGLE_API_KEY"]
GOOGLE_API_HOST=st.secrets["GOOGLE_API_HOST"]["GOOGLE_API_HOST"]

def fetch_google_trends():
    """
    Fetches Google Trends data from the API.
    
    Returns:
        dict: The JSON response from the API as a dictionary if successful.
        None: If the request fails.
    """
    headers = {
        "X-RapidAPI-Host": GOOGLE_API_HOST,
        "X-RapidAPI-Key": GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(GOOGLE_API_URL, headers=headers)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching Google Trends data: {e}")
        return None

# Example usage:
if __name__ == '__main__':
    trends_data = fetch_google_trends()
    if trends_data:
        print("Fetched Google Trends data successfully:")
    else:
        print("Failed to fetch Google Trends data.")
