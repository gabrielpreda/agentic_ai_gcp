from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions


DOCS_DIR = Path("docs")
DB_DIR = "vector_store"
COLLECTION_NAME = "enterprise_docs"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks


def load_documents() -> list[dict]:
    documents = []

    for path in DOCS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")

        for index, chunk in enumerate(chunk_text(text)):
            documents.append(
                {
                    "id": f"{path.stem}-{index}",
                    "text": chunk,
                    "source": path.name,
                    "chunk": index,
                }
            )

    return documents


def main():
    client = chromadb.PersistentClient(path=DB_DIR)

    embedding_function = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    documents = load_documents()

    collection.add(
        ids=[doc["id"] for doc in documents],
        documents=[doc["text"] for doc in documents],
        metadatas=[
            {
                "source": doc["source"],
                "chunk": doc["chunk"],
            }
            for doc in documents
        ],
    )

    print(f"Indexed {len(documents)} chunks.")


if __name__ == "__main__":
    main()