from google.adk.agents import Agent


def calculator(a: float, b: float, operation: str) -> float | str:
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        if b == 0:
            return "Cannot divide by zero. Please provide a non-zero divisor."
        return a / b

    raise Exception("Unsupported operation")


root_agent = Agent(
    name="assistant",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful assistant with calculator capabilities. "
        "Use the calculator tool for arithmetic. "
        "Supported operations are add, subtract, multiply, divide. "
        "If division by zero is requested, explain that it is undefined "
        "and ask the user for a non-zero divisor."
    ),
    tools = [calculator]
)