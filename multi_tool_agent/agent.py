from google.adk.agents import Agent


def calculator(a: float, b: float, operation: str) -> float:
    """
    Perform a basic arithmetic operation.

    Args:
        a: First number.
        b: Second number.
        operation: One of add, subtract, multiply, divide.
    """
    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    raise ValueError("Unsupported operation.")


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert values between simple supported units.

    Supported conversions:
    - km to miles
    - miles to km
    - celsius to fahrenheit
    - fahrenheit to celsius
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == "km" and to_unit == "miles":
        return value * 0.621371

    if from_unit == "miles" and to_unit == "km":
        return value / 0.621371

    if from_unit == "celsius" and to_unit == "fahrenheit":
        return value * 9 / 5 + 32

    if from_unit == "fahrenheit" and to_unit == "celsius":
        return (value - 32) * 5 / 9

    raise ValueError("Unsupported unit conversion.")


def get_weather_mock(city: str) -> dict:
    """
    Return mock weather data for a city.

    Args:
        city: City name.

    Returns:
        Weather information.
    """
    weather_data = {
        "bucharest": {
            "temperature_celsius": 23,
            "condition": "sunny",
            "wind_speed_kmh": 10,
        },
        "cluj": {
            "temperature_celsius": 21,
            "condition": "partly cloudy",
            "wind_speed_kmh": 8,
        },
        "london": {
            "temperature_celsius": 16,
            "condition": "rain",
            "wind_speed_kmh": 18,
        },
    }

    key = city.lower()

    if key not in weather_data:
        return {
            "city": city,
            "error": "Weather data not available for this city.",
        }

    return {
        "city": city,
        **weather_data[key],
    }


root_agent = Agent(
    name="multi_tool_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a practical assistant. "
        "Use the available tools when the user asks for calculations, "
        "unit conversions, or weather information. "
        "Explain the final answer briefly."
    ),
    tools=[
        calculator,
        convert_units,
        get_weather_mock,
    ],
)