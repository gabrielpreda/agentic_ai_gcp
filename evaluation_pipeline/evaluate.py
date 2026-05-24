import json
import re
import asyncio
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv


from agent import root_agent
from judge import run_rule_eval

load_dotenv()


BASE_DIR = Path(__file__).parent
TEST_CASES_PATH = BASE_DIR / "eval" / "test_cases.json"



async def run_agent(prompt: str) -> str:
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
            types.Part(text=prompt)
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

    return final_answer


async def main():
    with open(TEST_CASES_PATH) as f:
        test_cases = json.load(f)

    report = []

    for test_case in test_cases:
        
        # Step 1: run agent
        answer = await run_agent(test_case["prompt"])

        # Step 2: evaluate answer
        evaluation = run_rule_eval(
            test_case,
            answer,
        )

        # Step 3: update report
        report.append({
            "id": test_case["id"],
            "answer": answer,
            "passed": evaluation["passed"],
        })

    # Output report
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())