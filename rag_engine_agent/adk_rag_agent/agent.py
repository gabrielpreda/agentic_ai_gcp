# A 3-stage RAG SequentialAgent using Google ADK.
# Stage 1: Retriever -> Stage 2: Analyzer -> Stage 3: Final Answer

import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

from .prompts import (
        return_instructions_rag_retriever, 
        return_instructions_rag_writer
    )
# --------------------------------------------------------------------------------------
# Load environment variables (.env should already be created & have RAG_CORPUS, etc.)
# --------------------------------------------------------------------------------------
load_dotenv()
RAG_CORPUS = os.environ.get("RAG_CORPUS")
if not RAG_CORPUS:
    raise ValueError("RAG_CORPUS is not set. Make sure you've ingested and persisted the corpus name.")

GEMINI_MODEL = "gemini-2.5-pro"

# --------------------------------------------------------------------------------------
# Configure the Vertex AI RAG Retrieval tool (ADK tool)
# --------------------------------------------------------------------------------------
rag_retrieval_tool = VertexAiRagRetrieval(
    name="retrieve_ai_cymbal_pets_docs",
    description=(
        "Use this tool to retrieve information about pets care. "
        "Always call this tool before answering."
    ),
    rag_resources=[
        rag.RagResource(rag_corpus=RAG_CORPUS)
    ],
    # Tune these if needed; start conservative
    similarity_top_k=8,
    vector_distance_threshold=0.55,
)

# ======================================================================================
# 1) RAGRetrieverAgent
#    - Job: turn the user's question into a retrieval call, then return ONLY a compact
#      JSON structure of passages we’ll pass downstream.
# ======================================================================================
retriever_agent = LlmAgent(
    name="RAGRetrieverAgent",
    model=GEMINI_MODEL,
    description="Calls the RAG tool and returns normalized passages as JSON for downstream agents.",
    output_key="retrieved_passages_json",  # will be available to next agents via {retrieved_passages_json}
    tools=[rag_retrieval_tool],
    instruction=return_instructions_rag_retriever()
)


# ======================================================================================
# 2) RAGWriterAgent
#    - Job: write the final answer using the passages retrieved, with inline
#      numeric citations mapping to passage IDs (P1, P2, ...).
# ======================================================================================
writer_agent = LlmAgent(
    name="RAGWriterAgent",
    model=GEMINI_MODEL,
    description="Writes the final answer with citations to retrieved passages.",
    output_key="final_answer",  # the pipeline's final output
    instruction=return_instructions_rag_writer()
)

# ======================================================================================
# 3) Compose into a SequentialAgent
# ======================================================================================
root_agent = SequentialAgent(
    name="RAGPipelineAgent",
    sub_agents=[retriever_agent, writer_agent],
    description="RAG pipeline: Retriever -> Writer with citations.",
)

