from google.adk.agents import Agent


composer_instruction_prompt = """
You are an itinerary composer.

Given discovered places and route information, write a clear, friendly,
and concise travel itinerary.

Include:
- suggested order of visits
- estimated times
- practical notes
- helpful context

Use Markdown formatting.
"""


composer_agent = Agent(
    name="composer_agent",
    model="gemini-2.5-pro",
    description="Composes a readable travel itinerary.",
    instruction=composer_instruction_prompt,
    tools=[],
)