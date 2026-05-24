from google.adk.agents import Agent


def get_weather(city: str) -> dict:
    """Return simple demo weather data for a city."""

    weather_data = {
        "London": {
            "temperature": 18,
            "condition": "Cloudy",
        },
        "Paris": {
            "temperature": 21,
            "condition": "Sunny",
        },
        "Bucharest": {
            "temperature": 25,
            "condition": "Clear",
        },
    }


    return weather_data.get(
        city,
        {
            "temperature": None,
            "condition": "Unknown city",
        },
    )


root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a weather assistant.

    Use the get_weather tool when the user asks about weather.

    Explain the result clearly and briefly.
    """,
    tools=[
        get_weather,
    ],
)