import os
import logging

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


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("routing_agent")

logging.getLogger("google.adk").setLevel(logging.DEBUG)
logging.getLogger("google.adk.a2a").setLevel(logging.DEBUG)


logger.info("Loading environment variables...")
load_dotenv()

logger.info("Starting routing_agent module...")

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

logger.info("Creating local routing_agent...")

routing_agent = Agent(
    name="routing_agent",
    model="gemini-2.5-pro",
    description="Estimates routes and travel times using Google Maps grounding.",
    instruction=routing_instruction_prompt,
    tools=[google_maps_grounding],
)

logger.info(
    "Created routing_agent: name=%s model=%s tools=%s",
    routing_agent.name,
    "gemini-2.5-pro",
    ["google_maps_grounding"],
)


logger.info("Creating routing_agent_card...")

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

logger.info(
    "Created routing_agent_card: name=%s url=%s transport=%s",
    routing_agent_card.name,
    routing_agent_card.url,
    routing_agent_card.preferred_transport,
)


remote_agent_card_url = f"http://localhost:10021{AGENT_CARD_WELL_KNOWN_PATH}"

logger.info("Creating RemoteA2aAgent using card URL: %s", remote_agent_card_url)

remote_routing_agent = RemoteA2aAgent(
    name="routing_agent",
    description="Remote A2A routing agent.",
    agent_card=remote_agent_card_url,
)

logger.info("Created remote_routing_agent: name=%s", remote_routing_agent.name)


logger.info("Creating A2A server for routing_agent...")

a2a_app = create_agent_a2a_server(
    agent=routing_agent,
    agent_card=routing_agent_card,
)

logger.info("A2A server object created successfully")

application = a2a_app.build()

logger.info("A2A Starlette application built successfully")


def main():
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10021"))
    log_level = os.getenv("LOG_LEVEL", "debug")
    reload_enabled = os.getenv("RELOAD", "false").lower() == "true"

    logger.info(
        "Starting Routing Agent server on %s:%s | log_level=%s | reload=%s",
        host,
        port,
        log_level,
        reload_enabled,
    )

    uvicorn.run(
        "routing:application",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload_enabled,
        access_log=True,
    )


if __name__ == "__main__":
    main()