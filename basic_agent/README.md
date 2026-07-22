## Google Cloud Setup




Set the project and region:

```bash
export PROJECT_ID="gemini-first-439812"
export REGION="us-central1"
```

Authenticate:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project $PROJECT_ID
```

Enable required APIs:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  --project=$PROJECT_ID
```

---

## Create a Staging Bucket

Agent Runtime deployment needs a place to stage deployment artifacts.

```bash
export STAGING_BUCKET="gs://${PROJECT_ID}-agent-staging"

gsutil mb -l $REGION $STAGING_BUCKET
```

If the bucket already exists, reuse it.

---

## Deploy to Agent Runtime

Run this from the parent folder that contains `basic_agent/`.

```bash
adk deploy agent_engine basic_agent\
  --display_name="Basic Agent"\
  --project=$PROJECT_ID \
  --region=$REGION \
  --staging_bucket=$STAGING_BUCKET
```


This deploys the ADK agent project to Agent Runtime.

The deployment creates a managed agent resource, also called a Reasoning Engine resource in the API.

---

## Find the deployed agent

```bash
gcloud asset search-all-resources \
--scope=projects/$PROJECT_ID \
--asset-types='aiplatform.googleapis.com/ReasoningEngine' \
--format="table(name,assetType,location,reasoning_engine_id)"
```

Save the resource ID:

```bash
export RESOURCE_ID="your-reasoning-engine-id"
```

---

## Test the deployed agent with REST


```bash
curl \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}\
/locations/${REGION}/reasoningEngines/${RESOURCE_ID:query \
-d '{
"class_method": "async_create_session",
"input": {
"user_id": "demo_user"
}
}'
```

Copy the returned session id:

```bash
export SESSION_ID="returned-session-id"
```

Send a message to the deployed agent.


```bash
curl \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://${REGION}-
aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/reasoning
Engines/${RESOURCE_ID}:streamQuery?alt=sse \
-d '{
"class_method": "async_stream_query",
"input": {
"user_id": "demo_user",
"session_id": "'$SESSION_ID'",
"message": "Explain what an AI agent is in one paragraph."
}
}'
```
