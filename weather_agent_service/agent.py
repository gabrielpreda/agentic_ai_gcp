from google.adk.agents import Agent


import requests

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Depositing rime fog",

    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",

    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",

    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",

    66: "Light freezing rain",
    67: "Heavy freezing rain",

    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",

    77: "Snow grains",

    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",

    85: "Slight snow showers",
    86: "Heavy snow showers",

    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def get_weather(city: str) -> dict:
    """
    Get current weather for a supported city.

    Args:
        city: City name. Supported cities: Bucharest, Cluj, London, Tokyo.

    Returns:
        Current weather information including temperature, precipitation,
        wind speed, weather code, and description.
    """
    cities = {
        "bucharest": (44.4268, 26.1025),
        "london": (51.5074, -0.1278),
        "paris": (48.8566, 2.3522),
        "new york": (40.7128, -74.0060),
    }

    city_key = city.lower()

    if city_key not in cities:
        return {"error": f"Unknown city: {city}"}

    latitude, longitude = cities[city_key]

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current_weather=true"
    )

    response = requests.get(url)

    data = response.json()

    current = data.get("current_weather", {})
    print(current)

    weather_code = current.get("weathercode")

    return {
        "city": city,
        "time": current.get("time"),
        "temperature": current.get("temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "rain": current.get("rain"),
        "wind_speed": current.get("windspeed"),
        "wind_direction": current.get("winddirection"),
        "is_day": current.get("is_day"), 
        "weather_code": weather_code,
        "description": WEATHER_CODES.get(weather_code, 
                        f"Unknown weather code: {weather_code}"),
    }


root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    instruction="""
        "You are a helpful weather assistant. "
        "Use the weather tool whenever users ask about weather."
        "If you have access to wind direction, transform to wind rose direction"
        "Explain the result clearly and mention temperature, precipitation, "
        "wind speed, and general condition."
    """,
    tools=[
        get_weather,
    ],
)