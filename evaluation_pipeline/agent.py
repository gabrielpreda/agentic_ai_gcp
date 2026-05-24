import json
from pathlib import Path

from google.adk.agents import Agent


from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).parent

DATA_PATH = BASE_DIR / "data" / "sales.json"


def analyze_sales(question: str):

    sales = json.loads(
        DATA_PATH.read_text()
    )

    top_country = max(
        sales,
        key=lambda row: row["revenue"],
    )

    total_revenue = sum(
        row["revenue"]
        for row in sales
    )

    return {
        "top_country": top_country,
        "total_revenue": total_revenue,
        "rows": sales,
    }


root_agent = Agent(
    name="sales_analysis_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a sales analytics assistant.

    Use analyze_sales for revenue questions.

    Mention:
    - top country
    - country with top revenue
    - total revenue when relevant

    Do not invent values.
    """,
    tools=[
        analyze_sales,
    ],
)