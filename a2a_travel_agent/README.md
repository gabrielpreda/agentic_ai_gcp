# A2A Travel Agent

## Start the services

Open separate terminals.

Start the Discovery Agent A2A server:

```bash
uvicorn discovery:application --host 0.0.0.0 --port 10020
```

Start the Routing Agent A2A server:

```bash
uvicorn routing:application --host 0.0.0.0 --port 10021
```

Start the Host Travel Agent A2A server:

```bash
uvicorn agent:application --host 0.0.0.0 --port 10022
```

Start the FastAPI client:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Test the application

Send a request:

```bash
curl -X POST http://localhost:8000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I have 4 hours in Berlin. I like museums, architecture, and good coffee. Create a walking-friendly itinerary."
  }'
```

## Runtime flow

```mermaid
sequenceDiagram

participant User
participant Client as FastAPI Client
participant Host as Host A2A Agent
participant Discovery as Discovery A2A Agent
participant Routing as Routing A2A Agent
participant Composer as Composer Agent

User->>Client: POST /plan

Client->>Host: A2A message

Host->>Discovery: A2A call for places

Discovery-->>Host: Suggested places

Host->>Routing: A2A call for route

Routing-->>Host: Route and timing

Host->>Composer: Compose final itinerary

Composer-->>Host: Markdown itinerary

Host-->>Client: A2A task result

Client-->>User: JSON response
```