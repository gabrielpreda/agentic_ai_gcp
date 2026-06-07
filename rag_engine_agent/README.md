# Introduction

This project implements a combination of `SequentialAgent` and `LlmAgent` ADK agents, as following:
* **Retriever Agent** - `LlmAgent` - calls Vertex AI RAG to fetch contextually relevant passages from a structured corpus.
* **Analyzer Agent** - `LlmAgent` - interprets and summarizes retrieved text, highlighting key points, conflicts, and evidence.
* **Final Answer Agent** - `LlmAgent` - constructs a human-readable response with inline citations ([P1], [P2]), grounding every claim in the retrieved evidence.
* **root_agent** - `SequentialAgent` - orchestrate the 3 `LlmAgent` agents.

# Create the corpus and ingest data

Follow the steps:

1. Copy your data files in a GCP storage bucket, identified in the `.env` file as `GCS_URI`.
2. Set your `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` parameters in your `.env` file.
3. Set also `GOOGLE_GENAI_USE_VERTEXAI` to `True`.
4. Run:
    ```bash
    python adk-rag-agent/create_database/create_corpus_and_vector_database.py
    ```
    This will initialize the Vertex AI client, will create the corpus, download and upload to corpus the data.


# Running the Agent
You can run the agent using the ADK command in your terminal.
from the root project directory:

1.  Run agent in CLI:

    ```bash
    adk run adk-rag-agent
    ```

2.  Run agent with ADK Web UI:
    ```bash
    adk web
    ```
    
    Select the `adk-rag-agent` from the dropdown and start interogating the agents.

