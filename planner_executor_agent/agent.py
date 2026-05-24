import json
from pathlib import Path

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import AgentTool

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).parent

SALES_PATH = BASE_DIR / "data" / "sales.json"
POLICIES_PATH = BASE_DIR / "docs" / "policies.md"


def analyze_revenue() -> dict:
    """Analyze revenue data and return revenue insights."""

    sales = json.loads(SALES_PATH.read_text())

    top_market = max(
        sales,
        key=lambda row: row["revenue"],
    )

    total_revenue = sum(
        row["revenue"] for row in sales
    )

    return {
        "top_market": top_market,
        "total_revenue": total_revenue,
        "markets": sales,
    }


def retrieve_revenue_policies() -> dict:
    """Retrieve enterprise revenue reporting policies."""

    return {
        "policies": POLICIES_PATH.read_text()
    }


revenue_agent = Agent(
    name="revenue_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a revenue analytics specialist.

    Use only the analyze_revenue tool.

    Your job:
    - analyze revenue data
    - identify the top market
    - calculate total revenue
    - return concise business findings

    Do not answer policy questions.
    """,
    tools=[
        analyze_revenue,
    ],
)


policy_agent = Agent(
    name="policy_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a revenue policy specialist.

    Use only the retrieve_revenue_policies tool.

    Your job:
    - retrieve revenue reporting policies
    - summarize relevant reporting rules
    - identify governance requirements

    Do not perform revenue analysis.
    """,
    tools=[
        retrieve_revenue_policies,
    ],
)


planner_agent = Agent(
    name="planner_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the planning stage of a sequential workflow.

    Read the user request and create a short execution plan.

    The next stage is executor_agent.

    Your output must include:
    - the user goal
    - which specialist capabilities are needed
    - what executor_agent should do

    Do not call tools.
    Do not produce the final answer.
    """,
)


executor_agent = Agent(
    name="executor_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the execution stage of a sequential workflow.

    Use the plan produced by planner_agent.

    Delegate specialist work using:
    - revenue_agent for revenue, markets, and sales analysis
    - policy_agent for revenue policies and reporting rules

    Use AgentTool calls for specialist work.
    Do not generate the final report yourself.

    Return the execution results clearly so report_agent can analyze them.
    """,
    tools=[
        AgentTool(agent=revenue_agent),
        AgentTool(agent=policy_agent),
    ],
)


report_agent = Agent(
    name="report_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are the final reporting stage of a sequential workflow.

    Analyze the execution results from executor_agent.

    Your job:
    - verify whether the execution answered the user request
    - identify the revenue findings
    - identify the policy findings
    - compile the final business report

    Do not call tools.
    Do not invent missing data.

    If execution results are incomplete, state what is missing.

    Final report format:
    1. Execution summary
    2. Revenue findings
    3. Policy findings
    4. Final business conclusion
    """,
)


root_agent = SequentialAgent(
    name="planner_executor_report_workflow",
    sub_agents=[
        planner_agent,
        executor_agent,
        report_agent,
    ],
)