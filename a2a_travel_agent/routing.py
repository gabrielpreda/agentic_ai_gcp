import os

from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import google_maps_grounding
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

from agent_a2a_server import create_agent_a2a_server


load_dotenv()


routing_instruction_prompt = """
You are a routing agent.

Use Google Maps grounding to estimate routes and travel times
between a start location, destination, and optional waypoints.

Prefer walking when practical.
Use public transport when walking is not realistic.

Return:
- suggested route order
- estimated travel times
- useful movement notes
"""


routing_agent = Agent(
    name="routing_agent",
    model="gemini-2.5-pro",
    description="Estimates routes and travel times using Google Maps grounding.",
    instruction=routing_instruction_prompt,
    tools=[google_maps_grounding],
)


routing_agent_card = AgentCard(
    name="Routing Agent",
    url="http://localhost:10021",
    description="Uses Google Maps grounding to estimate routes and travel times.",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="routing_agent",
            name="Routing Agent",
            description="Plans route order and estimates travel time.",
            tags=[
                "travel",
                "routes",
                "maps",
                "walking",
                "transport",
                "distance",
            ],
            examples=[
                "Plan the best walking route between these places.",
                "How long does it take from the hotel to the museum?",
                "Suggest a route through these attractions.",
            ],
        )
    ],
)


remote_routing_agent = RemoteA2aAgent(
    name="routing_agent",
    description="Remote A2A routing agent.",
    agent_card=f"http://localhost:10021{AGENT_CARD_WELL_KNOWN_PATH}",
)


a2a_app = create_agent_a2a_server(
    agent=routing_agent,
    agent_card=routing_agent_card,
)

application = a2a_app.build()


def main():
    import uvicorn

    uvicorn.run(
        "routing:application",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "10021")),
        log_level=os.getenv("LOG_LEVEL", "info"),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()