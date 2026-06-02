import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent
from deepeval_judge import run_deepeval_eval

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
TEST_CASES_PATH = BASE_DIR / "eval" / "deepeval_test_cases.json"
REPORTS_DIR = BASE_DIR / "eval" / "reports"


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
        if event.is_final_response():
            final_answer = event.content.parts[0].text
            logger.info("Final answer=%r", final_answer)

    return final_answer


async def main():
    logger.info("Loading test cases from %s", TEST_CASES_PATH)

    with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc)

    report = {
        "started_at": started_at.isoformat(),
        "finished_at": None,
        "total_tests": len(test_cases),
        "passed_tests": 0,
        "failed_tests": 0,
        "results": [],
    }

    for test_case in test_cases:
        test_case_id = test_case["id"]

        logger.info("Starting test_case_id=%s", test_case_id)

        try:
            answer = await run_agent(test_case["prompt"])

            evaluation = run_deepeval_eval(
                test_case=test_case,
                answer=answer,
            )

            result = {
                "id": test_case_id,
                "prompt": test_case["prompt"],
                "expected_output": test_case.get("expected_output"),
                "answer": answer,
                "passed": evaluation["passed"],
                "rule_eval": evaluation["rule_eval"],
                "deepeval": evaluation["deepeval"],
            }

        except Exception as exc:
            logger.exception("Failed test_case_id=%s", test_case_id)

            result = {
                "id": test_case_id,
                "prompt": test_case["prompt"],
                "expected_output": test_case.get("expected_output"),
                "answer": None,
                "passed": False,
                "error": str(exc),
            }

        report["results"].append(result)

        if result["passed"]:
            report["passed_tests"] += 1
        else:
            report["failed_tests"] += 1

    finished_at = datetime.now(timezone.utc)
    accuracy = round(sum(1 if item.get("passed") else 0 for item in report["results"]) / len(report["results"]), 3)
    

    report["finished_at"] = finished_at.isoformat()
    report["duration_seconds"] = round(
        (finished_at - started_at).total_seconds(),
        2,
    )

    report_file = REPORTS_DIR / f"deepeval_report_{finished_at.strftime('%Y%m%d_%H%M%S')}.json"
    latest_report_file = REPORTS_DIR / "latest_deepeval_report.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    with open(latest_report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Test set accuracy: {accuracy}")
    logger.info("Wrote JSON report to %s", report_file)
    logger.info("Wrote latest JSON report to %s", latest_report_file)

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())