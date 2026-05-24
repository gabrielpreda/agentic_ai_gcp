# Objective

Learning Agentic AI with GCP - using ADK, A2A, Agent Platform, Agent Engine

# Highlights

- 🤖 Build intelligent agents with Gemini and the Google Agent Development Kit (ADK)
- 🛠️ Connect agents to tools, APIs, MCP servers, enterprise data, RAG pipelines, and BigQuery
- 🧩 Design multi-agent systems with orchestration, planning, reflection, A2A collaboration, and evaluation workflows
- ☁️ Deploy production-ready AI systems to Google Cloud using Cloud Run and Agent Engine
- 🔐 Learn enterprise-grade practices for security, observability, governance, and reliable agent operations

# Aplications

## Part 1 - Foundations of Agentic AI

| Resource | Description |
|---------|----------|
| [my_first_agent](my_first_agent) | My First ADK Agent |
| [calculator_agent](calculator_agent) | Tools Usage: Agent using calculator tool |
| [multi_tool_agent](multi_tool_agent) | Multi-tool Agent: calculator, weather, unit converter |
| [struct_calculator_agent](struct_calculator_agent) | Agent using structured output |
| [weather_agent](weather_agent) | Optional Tools Usage: Agent using tool with external API connection |


## Part 2 - Enterprise and Agent Patterns

| Resource | Description |
|----------|---------|
|  [enterprise-travel-agent](enterprise-travel-agent) | Multi-tool travel agent (include Agent as tools equiped with grounding tools & an API) |
|  [mcp_filesystem](mcp_filesystem) | Agent using a tool through an MCP server |
|  [enterprise-rag-agent](enterprise-rag-agent) | Enterprise RAG Assistant |
|  [mcp_biguery](mcp_bigquery) | BigQuery Analytics Agent - uses GCP MCP Server |


## Part 3 - Multi-Agent Systems

| Resource | Description |
|----------|---------|
|  [planner_executor_agent](planner_executor_agent) | Combination of deterministic sequence: planner-executor-reporter with dynamic routing using AgentTool by executor (uses two tools) |
|  [a2a_travel_agent](a2a_travel_agent) | Agent to Agent collaboration framework application: travel agent uses discovery and routing agents as services |
|  [evaluation_pipeline](evaluation_pipeline) | Evaluation using rule-based judge for an ADK Agent |


## Part 4 - Production and Governance

| Resource | Description |
|----------|---------|
|  [simple_agent_service](simple_agent_service) | Deploy an agent on Cloud Run to test with `adk web` |
|  [weather_agent_service](weather_agent_service) | Deploy an agent on Cloud Run with `FastAPI` |
|  [basic_agent](basic_agent) | Deploy an agent with Agent Engine |

