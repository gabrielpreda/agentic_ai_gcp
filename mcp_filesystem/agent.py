import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from dotenv import load_dotenv

load_dotenv()

filesystem_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "./data",
            ],
        ),
        timeout=30,
    )
)

root_agent = Agent(
    name="mcp_filesystem_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are an assistant with access to project files.

    Use MCP filesystem tools to:
    - inspect files
    - read documentation
    - summarize notes
    - explain project architecture

    Always explain which files you used.
    """,
    tools=[
        filesystem_tools,
    ],
)