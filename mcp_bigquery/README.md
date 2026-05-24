# BigQuery Analytics Agent

## Prerequisites

### 1. Configuration and environment

User roles:

* roles/bigquery.user (for running queries)
* roles/bigquery.dataViewer (for accessing data)
* roles/mcp.toolUser (for accessing MCP tools)
* roles/serviceusage.serviceUsageAdmin (for enabling apis)
* roles/iam.oauthClientViewer (oAuth)
* roles/iam.serviceAccountViewer (oAuth)
* roles/oauthconfig.editor (oAuth)

### 2. Project & auth config

```bash
BIGQUERY_PROJECT=PROJECT_ID
​
gcloud config set project ${BIGQUERY_PROJECT}
gcloud auth application-default login
```


### 3. User roles and APIs

```bash
gcloud services enable bigquery.googleapis.com --project=${BIGQUERY_PROJECT}
gcloud beta services mcp enable bigquery.googleapis.com --project=${BIGQUERY_PROJECT}
```

### 4. Load sample dataset

```bash
# Create the dataset if it doesn't exist (pick a location of your choice)
# You can add --default_table_expiration to auto expire tables.
bq --project_id=${BIGQUERY_PROJECT} mk -f --dataset --location=US cymbal_pets

# Load the data
for table in products customers orders order_items; do 
bq --project_id=${BIGQUERY_PROJECT} query --nouse_legacy_sql \
    "LOAD DATA OVERWRITE cymbal_pets.${table} FROM FILES(
        format = 'avro',
        uris = [ 'gs://sample-data-and-media/cymbal-pets/tables/${table}/*.avro']);"
done
```

### 5. Install Python packages

```bash
pip install -r requirements.txt
```

### 6. Set environment

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
Then select `bigquery_mcp_agent`.
