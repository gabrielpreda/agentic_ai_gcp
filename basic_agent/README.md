## Google Cloud Setup

Set the project and region:

```bash
export PROJECT_ID="your-project-id"
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
adk deploy agent_engine \
  --project=$PROJECT_ID \
  --region=$REGION \
  --staging_bucket=$STAGING_BUCKET \
  basic_agent
```

This deploys the ADK agent project to Agent Runtime.

The deployment creates a managed agent resource, also called a Reasoning Engine resource in the API.