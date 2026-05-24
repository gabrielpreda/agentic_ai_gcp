from google.adk.agents import Agent


root_agent = Agent(
    name="simple_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a helpful assistant.

    Answer clearly and concisely.
    """,
)