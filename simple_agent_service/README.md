# Simple agent deployed on Cloud Run

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
Then select `simple_agent`.

## Deploy on Cloud Run

Run: 

```bash
gcloud run deploy simple-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  --set-env-vars GOOGLE_CLOUD_LOCATION=us-central1
```
## Test on Cloud Run

```bash
gcloud run services describe simple-agent \
  --region us-central1 \
  --format='value(status.url)'
```

Open the returned URL in the browser.

The ADK web interface loads, and you can chat with `simple_agent`.
