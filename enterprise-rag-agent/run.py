import asyncio

import argparse

from google.genai import types

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent import root_agent


APP_NAME = "enterprise_rag_demo"
USER_ID = "demo-user"
SESSION_ID = "demo-session"


async def call_agent(prompt: str):
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=prompt),
        ],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content,
    ):
        if event.is_final_response():
            print("\n--- FINAL RESPONSE ---\n")
            print(event.content.parts[0].text)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True)

    args = parser.parse_args()  
    prompt = args.prompt

    if prompt:
        print("\n==============================")
        print(prompt)
        print("==============================")
        await call_agent(prompt)

    else:
        prompts = [
            "Where should we deploy lightweight ADK agents?",
            "What does the documentation say about BigQuery?",
            "What security controls are recommended for enterprise agents?",
            "Should production agents use broad owner permissions?",
        ]

        for prompt in prompts:
            print("\n==============================")
            print(prompt)
            print("==============================")

            await call_agent(prompt)


if __name__ == "__main__":
    asyncio.run(main())






    asyncio.run(main())