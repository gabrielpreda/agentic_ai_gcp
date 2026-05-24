import os

from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import google_search
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


discovery_instruction_prompt = """
You are a travel discovery agent.

Use Google Search to find relevant places and activities for a tourist
based on the user's location, available time, and interests.

Return a short list of places with concise explanations.

This output will be used later by the routing agent.
"""


discovery_agent = Agent(
    name="discovery_agent",
    model="gemini-2.5-pro",
    description="Uses Google Search to discover relevant places.",
    instruction=discovery_instruction_prompt,
    tools=[google_search],
)


discovery_agent_card = AgentCard(
    name="Discovery Agent",
    url="http://localhost:10020",
    description="Uses Google Search to discover relevant travel places.",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="discovery_agent",
            name="Discovery Agent",
            description="Discovers relevant locations and activities.",
            tags=[
                "travel",
                "locations",
                "landmarks",
                "museums",
                "restaurants",
                "activities",
            ],
            examples=[
                "What can I visit in Berlin in 4 hours?",
                "Find quiet museums and gardens in Paris.",
                "Suggest places to see near London Bridge.",
            ],
        )
    ],
)


remote_discovery_agent = RemoteA2aAgent(
    name="discovery_agent",
    description="Remote A2A discovery agent.",
    agent_card=f"http://localhost:10020{AGENT_CARD_WELL_KNOWN_PATH}",
)


a2a_app = create_agent_a2a_server(
    agent=discovery_agent,
    agent_card=discovery_agent_card,
)

application = a2a_app.build()


def main():
    import uvicorn

    uvicorn.run(
        "discovery:application",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "10020")),
        log_level=os.getenv("LOG_LEVEL", "info"),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()