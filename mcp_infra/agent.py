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

# Connect to Google's predefined Compute Engine MCP server endpoint
compute_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://compute.googleapis.com/mcp",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
)

# 1. Pull Compute Engine Tools
compute_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://compute.googleapis.com/mcp",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
)

# 2. Pull Resource Manager Tools (to view Cloud Run and overall project state)
resource_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://cloudresourcemanager.googleapis.com/mcp",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
)
compute_agent = Agent(
    name="compute_engine_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a dedicated Google Compute Engine (GCE) infrastructure specialist.
    
    Your sole responsibility is handling standalone virtual machines (VMs) and their hardware.
    Use your tools to:
    - Inspect, list, and check the status of virtual machine (VM) instances.
    - List available disks, zones, regions, and machine types.
    - Provide clear summaries of infrastructure health.

    Rules:
    - Never stop or delete virtual machines unless explicitly ordered by name.
    - Always state which zone or region you are inspecting.
    - Summarize resources clearly for DevOps teams.
    - If a user asks about project structures, folders, or serverless components (like Cloud Run), 
      politely state that it is out of your scope.
    """,
    tools=[compute_mcp_toolset]
)

resource_agent = Agent(
    name="resource_manager_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a dedicated Google Cloud Resource Manager specialist.
    
    Your sole responsibility is mapping project hierarchies and checking global scopes.
    Use your tools to:
    - Search, identify, and list Google Cloud projects, folders, or organizations.
    - Resolve missing context: search for projects matching a specific name or metadata.
    - Audit resource inventory, labels, and environment scopes (e.g., prod vs. staging).

    Rules:
    - Never attempt an infrastructure action without first verifying the correct, fully-qualified `projectId`. 
    - If a project search yields ambiguous or multiple results, ask the user for confirmation.
    - Translate technical resource states into clear business language for the operations team.
    - If a user asks about individual virtual machine metrics or disk attachments, 
      politely state that it is out of your scope.
    """,
    tools=[resource_mcp_toolset]
)

root_agent = Agent(
    name="gcp_cloud_architect",
    model="gemini-2.5-flash",
    instruction="""
    You are an enterprise Google Cloud architect and global coordinator.
    You do not execute API calls directly. Instead, delegate tasks to your sub-agents:
    - Use 'compute_engine_agent' for anything related to VMs, disks, and standalone instances.
    - Use 'resource_manager_agent' for project discoveries, organization hierarchies, and global audits.
    """,
    tools=[
        AgentTool(compute_agent),
        AgentTool(resource_agent)
    ]
)