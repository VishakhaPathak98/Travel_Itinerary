import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables from a .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
OpenAI_API_Key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("Weather_API_Key")
mapbox_api_key = os.getenv("MAPBOX_ACCESS_TOKEN")

client = OpenAI()


# Function to get latitude and longitude using Mapbox API
def get_lat_lon_mapbox(Destination):
    geocode_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{Destination}.json?access_token={mapbox_api_key}"
    response = requests.get(geocode_url)
    data = response.json()

    if response.status_code == 200 and 'features' in data and len(data['features']) > 0:
        lat = data['features'][0]['geometry']['coordinates'][1]
        lon = data['features'][0]['geometry']['coordinates'][0]
        return lat, lon
    else:
        return None, None


# Function to get weather forecast using OpenWeather API
def get_weather_forecast(lat, lon):
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
    response = requests.get(forecast_url)
    data = response.json()

    if response.status_code == 200:
        forecast = []
        for item in data['list']:
            forecast.append({
                'datetime': item['dt_txt'],
                'temp': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed']
            })
        return forecast
    else:
        return {"error": "Unable to fetch forecast data"}


# Function to get itinerary and integrate weather forecast with activity suggestions
def get_itinerary(Departure, Destination, Date, Duration, Budget, Currency, Food_Preferences, Activity, Hotel):
    # Get latitude and longitude of the destination
    lat, lon = get_lat_lon_mapbox(Destination)

    if lat is None or lon is None:
        return "Error: Unable to get location data for the destination."

    # Get the weather forecast for the destination
    weather_forecast = get_weather_forecast(lat, lon)

    if "error" in weather_forecast:
        return "Error: Unable to fetch weather data."

    # Create a summary of weather conditions
    weather_summary = []
    for forecast_item in weather_forecast:
        weather_summary.append({
            'datetime': forecast_item['datetime'],
            'temp': forecast_item['temp'],
            'description': forecast_item['description']
        })

    # Define the conversation flow for OpenAI to generate the itinerary
    messages = [
        {"role": "system",
         "content": "You are a helpful travel assistant, and you help me to plan my travel itinerary."},
        {"role": "user", "content": f"I am planning a trip. I am going to travel from {Departure} to {Destination}."},
        {"role": "user", "content": f"My starting date for travel is {Date}. My duration of traveling is {Duration}."},
        {"role": "user", "content": f"My budget for traveling is {Budget}. And the currency I am using is {Currency}."},
        {"role": "user", "content": f"My food preferences are {Food_Preferences}."},
        {"role": "user", "content": f"I want to do the following activities: {Activity}."},
        {"role": "user", "content": f"I prefer staying at {Hotel} hotels."},
        {"role": "user",
         "content": f"Here is the weather forecast for the destination:\n{', '.join([f'{item['datetime']}: {item['temp']}°C, {item['description']}' for item in weather_summary])}. Please suggest appropriate activities based on the weather forecast."},
        {"role": "user",
         "content": "Please provide a detailed, day-by-day itinerary, divided by morning, afternoon, evening, and night, with activities tailored to the weather (e.g., indoor activities for rainy weather, outdoor for sunny days)."
                    " For example, if the forecast predicts rain in the afternoon, you could suggest visiting a museum or going to a local cafe, and for sunny weather, you could suggest outdoor activities like hiking or sightseeing."
                    " Please format the itinerary as follows:\n\n"
                    "Day [X]: [Date]\n"
                    "  Morning: [Activity] - Weather: [Description, Temp °C]\n"
                    "  Afternoon: [Activity] - Weather: [Description, Temp °C]\n"
                    "  Evening: [Activity] - Weather: [Description, Temp °C]\n"
                    "  Night: [Activity] - Weather: [Description, Temp °C]\n\n"
                    "Example of the type of changes you should make based on weather forecast:\n"
                    " - If the forecast predicts rain, suggest indoor activities like visiting museums, watching a movie, cooking classes, or visiting a local art gallery.\n"
                    " - If the forecast predicts sunny weather, suggest outdoor activities like hiking, visiting parks, outdoor sightseeing tours, or beach activities.\n"
                    " - If the forecast predicts cloudy or mild weather, you could suggest a mix of both indoor and outdoor activities.\n\n"
                    "Please follow this format for each day of the itinerary."}
    ]

    # OpenAI chat API to generate the itinerary
    response = client.chat.completions.create(model='gpt-3.5-turbo', messages=messages, max_tokens=4000,
                                              temperature=0.9)
    itinerary = response.choices[0].message.content.strip()

    # Add the weather forecast to the itinerary (for context)
    weather_info = "\n\n**Weather Forecast for your destination:**\n"
    for forecast_item in weather_forecast:
        weather_info += f"{forecast_item['datetime']} - Temp: {forecast_item['temp']}°C, {forecast_item['description']}, Humidity: {forecast_item['humidity']}%, Wind Speed: {forecast_item['wind_speed']} m/s\n"

    # Combine the itinerary and weather forecast
    final_itinerary = f"{itinerary}"

    return final_itinerary


