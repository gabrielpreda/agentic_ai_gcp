import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "sales.json"


def analyze_sales(question: str):
    logger.info("analyze_sales called with question=%r", question)
    logger.info("Loading sales data from %s", DATA_PATH)

    sales = json.loads(DATA_PATH.read_text())

    logger.info("Loaded %d sales rows", len(sales))

    top_country = max(
        sales,
        key=lambda row: row["revenue"],
    )

    total_revenue = sum(
        row["revenue"]
        for row in sales
    )

    logger.info(
        "Computed sales summary: top_country=%s top_revenue=%s total_revenue=%s",
        top_country["country"],
        top_country["revenue"],
        total_revenue,
    )

    return {
        "top_country": top_country,
        "total_revenue": total_revenue,
        "rows": sales,
    }

simple_instructions = """
    You are a sales analytics assistant.

    Use analyze_sales for revenue questions.

    Mention:
    - top country
    - country with top revenue
    - total revenue when relevant

    Do not invent values.
    """

improved_instructions = """
    You are a sales analytics assistant.

    Use analyze_sales for revenue questions.

    Only answer what the user asked. Observe closely the rules listed below.
    Do not add extra countries, totals, rankings, or explanations unless directly relevant.

    Rules:
    - For highest/top revenue questions: mention the top country and its revenue. Do not mention 
    overal total.
    - For total revenue questions: mention only the total revenue. Do not mention top country or
    top revenue.
    - For lowest revenue questions: mention only the lowest country and its revenue. Do not mention
    total revenue or top revenue country.
    - For ranking questions: list countries in revenue order.
    - For presence/lookup questions, answer whether the country exists in the data.

    Do not invent values.
    """

root_agent = Agent(
    name="sales_analysis_agent",
    model="gemini-2.5-flash",
    instruction=improved_instructions,
    tools=[
        analyze_sales,
    ],
)