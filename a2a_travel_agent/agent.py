import os
import logging

from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)

from agent_a2a_server import create_agent_a2a_server
from composer import composer_agent
from discovery import remote_discovery_agent
from routing import remote_routing_agent



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("travel_agent")

load_dotenv()


logger.info("Loading Travel Assistant Agent...")

host_instruction_prompt = """
You are a travel coordinator agent.

Your job is to create a practical travel itinerary for the user.

You have access to three agent tools:

1. discovery_agent
   - Use it first to discover relevant places and activities.

2. routing_agent
   - Use it after discovery to organize places into a realistic route.

3. composer_agent
   - Use it last to create a clear final itinerary.

Do not ask the user for confirmation before using tools.
Do not create a long conversation.
Produce one useful itinerary directly.

Prefer:
- practical plans
- realistic travel times
- walkable routes where possible
- concise Markdown output
"""


root_agent = Agent(
    name="a2a_travel_assistant",
    model="gemini-2.5-pro",
    description="Coordinates remote discovery and routing agents to plan a smart trip.",
    instruction=host_instruction_prompt,
    tools=[
        AgentTool(agent=remote_discovery_agent),
        AgentTool(agent=remote_routing_agent),
        AgentTool(agent=composer_agent),
    ],
)


root_agent_card = AgentCard(
    name="A2A Travel Assistant",
    url="http://localhost:10022",
    description="Coordinates discovery, routing, and itinerary composition.",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="a2a_travel_assistant",
            name="A2A Travel Assistant",
            description="Plans local travel itineraries using remote A2A agents.",
            tags=[
                "travel",
                "itinerary",
                "a2a",
                "maps",
                "search",
                "routing",
            ],
            examples=[
                "Plan a 4-hour visit in Berlin with museums and cafes.",
                "I have half a day in Paris and like art and quiet gardens.",
                "Create a walking-friendly itinerary around central London.",
            ],
        )
    ],
)

logger.info(
    "Agent Card created. URL=%s, Transport=%s",
    root_agent_card.url,
    root_agent_card.preferred_transport,
)

logger.info("Creating A2A server...")

a2a_app = create_agent_a2a_server(
    agent=root_agent,
    agent_card=root_agent_card,
)

logger.info("A2A server created successfully")

application = a2a_app.build()

logger.info("Starlette application built")


def main():
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10022"))

    logger.info(
        "Starting Travel Agent on %s:%s",
        host,
        port,
    )

    uvicorn.run(
        "agent:application",
        host=host,
        port=port,
        log_level=os.getenv("LOG_LEVEL", "debug"),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()