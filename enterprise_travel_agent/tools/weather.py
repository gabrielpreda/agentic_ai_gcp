import requests

def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city}?format=3"

    response = requests.get(url)

    return response.text