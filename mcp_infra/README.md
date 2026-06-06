# GCP Infra Agent

## Prerequisites

### 1. Configuration and environment

User roles:

* roles/mcp.toolUser (for accessing MCP tools)
* roles/serviceusage.serviceUsageAdmin (for enabling apis)
* roles/iam.oauthClientViewer (oAuth)
* roles/iam.serviceAccountViewer (oAuth)
* roles/oauthconfig.editor (oAuth)

### 2. Project & auth config

```bash
STORAGE_PROJECT=PROJECT_ID
​
gcloud config set project ${STORAGE_PROJECT}
gcloud auth application-default login
```


### 3. User roles and APIs

```bash
gcloud services enable storage.googleapis.com
gcloud beta services mcp enable storage.googleapis.com --project=${STORAGE_PROJECT}
```


### 4. Install Python packages

```bash
pip install -r requirements.txt
```

### 5. Set environment

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
Then select `mcp_storage`.
