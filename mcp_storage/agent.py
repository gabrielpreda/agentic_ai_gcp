import os
import subprocess
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)

load_dotenv()

def get_access_token() -> str:
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

access_token = get_access_token()

storage_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://storage.googleapis.com/storage/mcp",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
)

root_agent = Agent(
    name="cloud_storage_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a dedicated Google Cloud Storage (GCS) specialist.
    
    Your sole responsibility is handling storage buckets and object data configurations.
    Use your tools to:
    - List all Google Cloud Storage buckets within the designated project.
    - Inspect bucket properties, locations (regions/multi-regions), and storage classes (e.g., Standard, Nearline, Coldline, Archive).
    - Check object counts, bucket access controls, or lifecycle management policies if requested.

    Rules:
    - Never delete or empty a storage bucket unless explicitly ordered by its exact name with confirmation.
    - Always report the location/region of the buckets you discover.
    - Present bucket lists cleanly, highlighting active configurations or public access risks for the security team.
    - If a user asks about Compute Engine VMs, running containers, or project hierarchies, 
      politely state that it is out of your scope.
    """,
    tools=[storage_mcp_toolset],
)