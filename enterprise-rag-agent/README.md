# Enterprise RAG Agent

## Prerequisites

### 1. Install Python packages

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
This will install the packages:

```text
google-adk
google-genai
python-dotenv
chromadb
```

### 2. Setup the environment

```bash
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=PROJECT_ID
GOOGLE_CLOUD_LOCATION=MY_REGION
```

### 3. Create Demo Files

```bash
mkdir -p enterprise-rag-agent/docs
mkdir -p enterprise-rag-agent/vector_store
cd enterprise-rag-agent
```

```bash
cat > docs/cloud_run.md <<'EOF'
# Cloud Run Deployment

The recommended deployment target for lightweight ADK agents is Cloud Run.

Cloud Run provides:
- container-based deployment
- autoscaling
- HTTPS endpoints
- simple integration with IAM

For production systems, store secrets in Secret Manager.
EOF
```

```bash
cat > docs/bigquery.md <<'EOF'
# BigQuery Analytics

BigQuery is used for enterprise analytics workloads.

Agents can use BigQuery to:
- inspect datasets
- query structured data
- summarize business metrics
- support analytics copilots

SQL access should be read-only in production.
EOF
```

```bash
cat > docs/security.md <<'EOF'
# Agent Security

Enterprise agents must follow least privilege.

Recommended controls:
- IAM-based access
- read-only permissions where possible
- Secret Manager for credentials
- query validation
- audit logging
- human approval for sensitive actions
EOF
```


## Ingest documents

Run:

```bash
python ingest.py
```

### Run tests

```bash
python run.py
```