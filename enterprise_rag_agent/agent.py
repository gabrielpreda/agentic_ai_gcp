import chromadb

from dotenv import load_dotenv

from chromadb.utils import embedding_functions
from google.adk.agents import Agent


load_dotenv()


DB_DIR = "vector_store"
COLLECTION_NAME = "enterprise_docs"


client = chromadb.PersistentClient(path=DB_DIR)

print(client)

embedding_function = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function,
)


def retrieve_documents(query: str, top_k: int = 3) -> dict:
    """
    Retrieve relevant enterprise documentation chunks.

    Args:
        query: The user question or search query.
        top_k: Number of chunks to retrieve.

    Returns:
        Relevant chunks with source metadata.
    """

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
    )

    chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    for text, metadata in zip(documents, metadatas):
        chunks.append(
            {
                "source": metadata["source"],
                "chunk": metadata["chunk"],
                "text": text,
            }
        )

    return {
        "query": query,
        "results": chunks,
    }


root_agent = Agent(
    name="enterprise_rag_assistant",
    model="gemini-2.5-flash",
    instruction="""
    You are an enterprise RAG assistant.

    Use retrieve_documents whenever the user asks about:
    - deployment
    - BigQuery
    - security
    - production architecture
    - enterprise agent practices

    Rules:
    - Ground answers in retrieved documents.
    - Mention the source file names.
    - If the retrieved context is insufficient, say so.
    - Do not invent policies that are not in the documents.
    """,
    tools=[
        retrieve_documents,
    ],
)