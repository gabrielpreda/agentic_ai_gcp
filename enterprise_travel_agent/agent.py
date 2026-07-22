from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools import google_maps_grounding
from google.adk.tools.agent_tool import AgentTool

from .tools.weather import get_weather


routing_instruction_prompt = """
    You are a routing agent. Use the google_maps_grounding 
    tool to estimate the best route and travel times 
    between a start and destination with optional waypoints.
    You can use the tool: google_maps_grounding.
    Walking is preferable but local transportation 
    is also acceptable, if available.
"""

routing_agent = LlmAgent(
    name="routing_agent",
    model="gemini-2.5-pro",
    description=(
        "Estimates an optimal travel route using ADK v1.15+ google_maps_grounding tool."
    ),
    instruction=routing_instruction_prompt,
    tools=[google_maps_grounding],
)


discovery_instruction_prompt = """
    You are a travel discovery agent. 
    Use Google Search to find the most relevant 
    places and activities for a tourist,
    based on given location and interests. 
    Return a short list or paragraph.
    Note: this list will be used further by the routing Agent.
    """

discovery_agent = LlmAgent(
    name="discovery_agent",
    model="gemini-2.5-pro",
    description="Uses Google Search to discover relevant places.",
    instruction=discovery_instruction_prompt,
    tools=[google_search]
)

composer_instruction_prompt = """
    You are an itinerary composer. 
    Given a route and points of interest, write a clear, 
    friendly and concise itinerary
    for a tourist. 
    Include times, locations, and helpful context.
    """

composer_agent = LlmAgent(
    name="composer_agent",
    model="gemini-2.5-pro",
    description="Composes a readable travel itinerary from discovery and routing information.",
    instruction=composer_instruction_prompt,
    tools=[]  # no tools needed for this agent
)

root_agent_instructions="""
        You are a travel agent specialized
        in planning short city explorations.
        You can use the discovery agent to identify interesting places,
        the routing agent to plan the itinerary, weather tool to 
        check the weather, and composer agent to summarize the
        travel itinerary based on the information gathered by the
        other agents.
        """
root_agent = LlmAgent(
    name="travel_agent",
    model="gemini-2.5-pro",
    description="Travel planning assistant",
    instruction=root_agent_instructions,
    tools=[
        AgentTool(discovery_agent),
        AgentTool(routing_agent),
        get_weather,
        AgentTool(composer_agent)
    ]
)