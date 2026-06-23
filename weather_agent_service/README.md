# Weather agent  deployed on Cloud Run

## Prerequisites

### Set environment

Create .env file with:

```bash
GOOGLE_CLOUD_PROJECT=PROJECT_ID
GOOGLE_CLOUD_LOCATION=MY_REGION
GOOGLE_GENAI_USE_VERTEXAI=True
```

## Run locally

Run:

```bash
adk web
```
Then select `weather_agent_service`.

## Deploy on Cloud Run

Run: 

```bash
gcloud run deploy weather-agent-service \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE \
  --set-env-vars GOOGLE_CLOUD_PROJECT=gemini-first-439812 \
  --set-env-vars GOOGLE_CLOUD_LOCATION=us-central1
```
## Test on Cloud Run

```bash
gcloud run services describe weather-agent-service \
  --region us-central1 \
  --format='value(status.url)'
```

Open the returned URL in the browser.

