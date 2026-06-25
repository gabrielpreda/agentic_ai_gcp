from google.adk.agents import Agent
from pydantic import BaseModel


class CalculationResult(BaseModel):
    operation: str
    a: float
    b: float
    result: float = None
    explanation: str


def calculator(a: float, b: float, operation: str) -> dict:

    if operation == "add":
        result = a + b

    elif operation == "subtract":
        result = a - b

    elif operation == "multiply":
        result = a * b

    elif operation == "divide":

        if b == 0:
            return {
                "operation": operation,
                "a": a,
                "b": b,
                "result": None,
                "explanation": "Cannot divide by zero."
            }

        result = a / b

    else:
        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": None,
            "explanation": "Unsupported operation."
        }

    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result,
        "explanation": f"The result of {operation} is {result}."
    }


root_agent = Agent(
    name="structured_calculator_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a calculator assistant. "
        "Use the calculator tool for arithmetic. "
        "Supported operations are add, subtract, multiply, divide."
        "Return the final answer using the required schema."
    ),
    tools=[calculator],
    output_schema=CalculationResult,
)