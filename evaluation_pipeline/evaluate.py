import asyncio
import json
import logging
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent
from judge import run_rule_eval

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
TEST_CASES_PATH = BASE_DIR / "eval" / "test_cases.json"


async def run_agent(prompt: str) -> str:
    logger.info("Running agent with prompt=%r", prompt)

    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name="eval_app",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="eval_app",
        user_id="eval_user",
    )

    logger.info("Created eval session session_id=%s", session.id)

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=prompt),
        ],
    )

    final_answer = ""

    async for event in runner.run_async(
        user_id="eval_user",
        session_id=session.id,
        new_message=content,
    ):
        logger.debug("Received event: %s", event)

        if event.is_final_response():
            final_answer = event.content.parts[0].text
            logger.info("Final agent answer=%r", final_answer)

    return final_answer


async def main():
    logger.info("Loading test cases from %s", TEST_CASES_PATH)

    with open(TEST_CASES_PATH) as f:
        test_cases = json.load(f)

    logger.info("Loaded %d test cases", len(test_cases))

    report = []

    for test_case in test_cases:
        test_case_id = test_case["id"]

        logger.info("Starting test_case_id=%s", test_case_id)

        try:
            answer = await run_agent(test_case["prompt"])

            evaluation = run_rule_eval(
                test_case,
                answer,
            )

            report.append({
                "id": test_case_id,
                "prompt": test_case["prompt"],
                "answer": answer,
                "passed": evaluation["passed"],
                "missing_keywords": evaluation["missing_keywords"],
                "forbidden_matches": evaluation["forbidden_matches"],
            })

            logger.info(
                "Finished test_case_id=%s passed=%s",
                test_case_id,
                evaluation["passed"],
            )

        except Exception:
            logger.exception("Test case failed with exception test_case_id=%s", test_case_id)

            report.append({
                "id": test_case_id,
                "prompt": test_case["prompt"],
                "answer": None,
                "passed": False,
                "error": "Exception occurred. Check logs for details.",
            })

    print(json.dumps(report, indent=2))
    accuracy = round(sum(1 if item.get("passed") else 0 for item in report) / len(report), 3)
    print(f"Test set accuracy: {accuracy}")

if __name__ == "__main__":
    asyncio.run(main())