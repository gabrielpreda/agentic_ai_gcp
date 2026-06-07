import logging
import os

import google.auth
from google.auth.transport.requests import Request
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logging.getLogger("google.adk").setLevel(logging.DEBUG)
logging.getLogger("google.adk.tools").setLevel(logging.DEBUG)
logging.getLogger("google.adk.tools.mcp_tool").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-2.5-flash")


def get_access_token() -> str:
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token


def create_storage_mcp_toolset() -> MCPToolset:
    logger.info("Creating Cloud Storage MCP toolset with fresh access token")

    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://storage.googleapis.com/storage/mcp",
            headers={
                "Authorization": f"Bearer {get_access_token()}",
            },
        )
    )


root_agent = Agent(
    name="cloud_storage_agent",
    model=MODEL_NAME,
    instruction="""
    You are a dedicated Google Cloud Storage specialist.

    Use your tools to list buckets, inspect bucket properties,
    report locations, storage classes, access controls,
    lifecycle policies, and object information when requested.

    Never delete or empty a bucket unless explicitly ordered
    by exact bucket name with confirmation.

    Always report bucket location or region.

    If the user asks about Compute Engine, containers,
    or project hierarchy, say that it is out of scope.
    """,
    tools=[
        create_storage_mcp_toolset(),
    ],
)