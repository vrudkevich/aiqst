import os

import requests as req
from dotenv import load_dotenv

load_dotenv()

def get_users():
    users_endpoint = os.getenv('USERS_ENDPOINT')

    if not users_endpoint:
        raise ValueError("USERS_ENDPOINT environment variable is not set")

    try:
        response = req.get(users_endpoint)
        response.raise_for_status() 
        return response.json()
    except req.RequestException as e:
        raise ValueError(f"Error making API request: {e}")
    
    
def get_weather(lat, lon):
    api_key = os.getenv('WEATHER_APIKEY')
    endpoint = os.getenv('WEATHER_ENDPOINT')

    if not api_key:
        raise ValueError("WEATHER_APIKEY environment variable is not set")
    if not endpoint:
        raise ValueError("WEATHER_ENDPOINT environment variable is not set")
    
    try:
        response = req.get(f"{endpoint}?units=metric&lat={lat}&lon={lon}&appid={api_key}")
        response.raise_for_status() 
        return response.json()
    except req.RequestException as e:
        raise ValueError(f"Error making API request: {e}")