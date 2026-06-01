import logging
import time
from typing import Any

import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel

from a2a.client import ClientConfig, ClientFactory, create_text_message_object
from a2a.types import AgentCard, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("fastapi_client")

logging.getLogger("a2a").setLevel(logging.DEBUG)
logging.getLogger("google.adk").setLevel(logging.DEBUG)
logging.getLogger("google.adk.a2a").setLevel(logging.DEBUG)


load_dotenv()


HOST_AGENT_URL = "http://localhost:10022"


class A2ASimpleClient:
    def __init__(self, default_timeout: float = 240.0):
        self._agent_info_cache: dict[str, dict[str, Any] | None] = {}
        self.default_timeout = default_timeout
        logger.info("A2ASimpleClient initialized with timeout=%ss", default_timeout)

    async def create_task(self, agent_url: str, message: str) -> str:
        logger.info("Starting A2A task")
        logger.info("Target agent URL: %s", agent_url)
        logger.info("User message: %s", message)

        timeout_config = httpx.Timeout(
            timeout=self.default_timeout,
            connect=10.0,
            read=self.default_timeout,
            write=10.0,
            pool=5.0,
        )

        try:
            async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
                if agent_url in self._agent_info_cache:
                    logger.info("Using cached agent card for %s", agent_url)
                    agent_card_data = self._agent_info_cache[agent_url]
                else:
                    agent_card_url = f"{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}"
                    logger.info("Fetching agent card from: %s", agent_card_url)

                    agent_card_response = await httpx_client.get(agent_card_url)

                    logger.info(
                        "Agent card response status: %s",
                        agent_card_response.status_code,
                    )

                    agent_card_response.raise_for_status()
                    agent_card_data = agent_card_response.json()
                    self._agent_info_cache[agent_url] = agent_card_data

                    logger.debug("Agent card data: %s", agent_card_data)

                logger.info("Creating AgentCard object")
                agent_card = AgentCard(**agent_card_data)

                logger.info(
                    "Agent card loaded: name=%s url=%s transport=%s",
                    agent_card.name,
                    agent_card.url,
                    agent_card.preferred_transport,
                )

                config = ClientConfig(
                    httpx_client=httpx_client,
                    supported_transports=[
                        TransportProtocol.jsonrpc,
                        TransportProtocol.http_json,
                    ],
                    use_client_preference=True,
                )

                logger.info("Creating A2A client")
                factory = ClientFactory(config)
                client = factory.create(agent_card)

                logger.info("Creating text message object")
                message_obj = create_text_message_object(content=message)

                responses = []

                logger.info("Sending message to A2A agent...")

                async for response in client.send_message(message_obj):
                    logger.info("Received A2A response chunk: %s", type(response))
                    logger.debug("A2A response chunk content: %s", response)
                    responses.append(response)

                logger.info("A2A response stream completed. chunks=%s", len(responses))

                if responses and isinstance(responses[0], tuple):
                    task = responses[0][0]

                    logger.info("Received task object: %s", type(task))
                    logger.debug("Task content: %s", task)

                    try:
                        text = task.artifacts[0].parts[0].root.text
                        logger.info("Extracted response text successfully")
                        logger.debug("Response text: %s", text)
                        return text
                    except (AttributeError, IndexError) as exc:
                        logger.exception("Could not extract text from task: %s", exc)
                        return str(task)

                logger.warning("No valid response received from A2A agent")
                return "No response received."

        except httpx.TimeoutException:
            logger.exception("A2A request timed out")
            raise

        except httpx.HTTPStatusError:
            logger.exception("A2A HTTP error")
            raise

        except Exception:
            logger.exception("Unexpected error while creating A2A task")
            raise


a2a_client = A2ASimpleClient()

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()

    logger.info("HTTP request started: %s %s", request.method, request.url.path)

    try:
        response = await call_next(request)
        duration = time.time() - start

        logger.info(
            "HTTP request completed: %s %s -> %s in %.2fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        return response

    except Exception:
        duration = time.time() - start
        logger.exception(
            "HTTP request failed: %s %s after %.2fs",
            request.method,
            request.url.path,
            duration,
        )
        raise


class TripRequest(BaseModel):
    query: str


@app.post("/plan")
async def plan_trip(request: TripRequest):
    logger.info("Received /plan request")
    logger.info("Query: %s", request.query)

    response_text = await a2a_client.create_task(
        HOST_AGENT_URL,
        request.query,
    )

    logger.info("Returning itinerary response. chars=%s", len(response_text))

    return {
        "itinerary": response_text
    }