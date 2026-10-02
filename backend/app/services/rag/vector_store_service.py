from pathlib import Path

import chromadb

from app.services.rag.embedding_service import generate_embeddings


CHROMA_DIR = Path("chroma_db")

COLLECTION_NAME = "company_documents"


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": "Enterprise AI Assistant company documents"
    }
)


def add_documents(
    documents: list[dict]
) -> None:
    """
    Add RAG documents to ChromaDB.
    """

    if not documents:
        return

    texts = [
        document["text"]
        for document in documents
    ]

    embeddings = generate_embeddings(texts)

    ids = [
        f"{document['metadata']['filename']}"
        f"_{index}"
        for index, document in enumerate(documents)
    ]

    metadatas = [
        document["metadata"]
        for document in documents
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def get_collection_count() -> int:
    """
    Return number of documents stored in ChromaDB.
    """

    return collection.count()


def clear_collection() -> None:
    """
    Delete all documents from the collection.
    """

    existing = collection.get()

    ids = existing.get("ids", [])

    if ids:
        collection.delete(ids=ids)