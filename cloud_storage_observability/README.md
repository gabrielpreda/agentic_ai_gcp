# Cloud run observability

## Cloud Run Service Account
Create or choose a service account for the deployed agent.


```bash
PROJECT_ID=YOUR_PROJECT_ID
SERVICE_ACCOUNT_EMAIL=YOUR_SERVICE_ACCOUNT_EMAIL
```
Grant it read-only access to Cloud Storage:

```bash
gcloud services enable storage.googleapis.com \
  --project  $PROJECT_ID
```

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.viewer"
```

For Vertex AI / Gemini access, also grant the required Vertex AI permissions:


```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/aiplatform.user"
```

MCP User Role

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/mcp.toolUser"
```



## Deploy to Cloud Run


```bash
gcloud run deploy cloud-storage-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account SERVICE_ACCOUNT_EMAIL \
   --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_PROJECT=PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,AGENT_MODEL=gemini-2.5-flash
```
