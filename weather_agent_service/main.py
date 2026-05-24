import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name="weather_agent_service",
    session_service=session_service,
)


class QueryRequest(BaseModel):
    message: str


@app.get("/status")
def status():
    return {
        "status": "ok"
    }


@app.post("/weather")
async def weather(request: QueryRequest):
    user_id = "api_user"
    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name="weather_agent_service",
        user_id=user_id,
        session_id=session_id,
    )

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=request.message)
        ],
    )

    final_answer = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            final_answer = event.content.parts[0].text

    return {
        "response": final_answer
    }