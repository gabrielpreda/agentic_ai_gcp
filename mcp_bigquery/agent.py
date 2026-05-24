import os
import subprocess

from dotenv import load_dotenv

from google.adk.agents import Agent
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

bigquery_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://bigquery.googleapis.com/mcp",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
)

root_agent = Agent(
    name="bigquery_mcp_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a BigQuery analytics assistant.

    Use the BigQuery MCP tools to:
    - inspect projects, datasets, tables, and schemas
    - generate analytical SQL
    - run safe read-only queries
    - summarize results clearly

    Rules:
    - Prefer SELECT queries.
    - Do not run destructive SQL.
    - Ask for clarification if the dataset or table is ambiguous.
    - Explain the result in business language.
    """,
    tools=[
        bigquery_mcp_toolset,
    ],
)