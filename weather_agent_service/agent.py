from google.adk.agents import Agent
from dotenv import load_dotenv
import requests
import logging
load_dotenv()



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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logging.getLogger("google.adk").setLevel(logging.DEBUG)
logging.getLogger("google.adk.tools").setLevel(logging.DEBUG)
logging.getLogger("google.adk.tools.mcp_tool").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

def get_weather(city: str) -> dict:
    """
    Get current weather for a supported city.

    Args:
        city: City name. Supported cities:
        Romania
         - Bucharest, Cluj-Napoca, Timișoara, Iași, Brașov, Constanța
        Europe
         - London, Paris, Berlin, Madrid, Rome, Amsterdam, Vienna, Athens, Istanbul
        Rest of the world
        -   New York, Los Angeles, Toronto, Mexico City, São Paulo, Tokyo, Beijing, Mumbai, Sydney

    Returns:
        Current weather information including temperature, precipitation,
        wind speed, weather code, and description.
    """
    cities = {
        # Romania
        "bucharest": (44.4268, 26.1025),
        "cluj-napoca": (46.7712, 23.6236),
        "timisoara": (45.7489, 21.2087),
        "iasi": (47.1585, 27.6014),
        "brasov": (45.6579, 25.6012),
        "constanta": (44.1598, 28.6348),

        # Europe
        "london": (51.5074, -0.1278),
        "paris": (48.8566, 2.3522),
        "berlin": (52.5200, 13.4050),
        "madrid": (40.4168, -3.7038),
        "rome": (41.9028, 12.4964),
        "amsterdam": (52.3676, 4.9041),
        "vienna": (48.2082, 16.3738),
        "athens": (37.9838, 23.7275),
        "istanbul": (41.0082, 28.9784),

        # Rest of the world
        "new york": (40.7128, -74.0060),
        "los angeles": (34.0522, -118.2437),
        "toronto": (43.6532, -79.3832),
        "mexico city": (19.4326, -99.1332),
        "sao paulo": (-23.5505, -46.6333),
        "tokyo": (35.6762, 139.6503),
        "beijing": (39.9042, 116.4074),
        "mumbai": (19.0760, 72.8777),
        "sydney": (-33.8688, 151.2093),
    }

    city_key = city.lower()

    if city_key not in cities:
        logger.error(f"get_weather city not in cities: {city_key}")
        return {"error": f"Unknown city: {city}"}

    latitude, longitude = cities[city_key]
    logger.info(f"get_weather latitude: {latitude} longitude: {longitude}")

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current_weather=true"
    )

    response = requests.get(url)

    logger.info(f"get_weather response: {response}")
    

    data = response.json()

    logger.info(f"get_weather data: {data}")

    current = data.get("current_weather", {})
    print(current)

    weather_code = current.get("weathercode")

    logger.info(f"get_weather weather code: {weather_code}")

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