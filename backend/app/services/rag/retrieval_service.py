from app.services.rag.embedding_service import generate_embedding
from app.services.rag.vector_store_service import collection


def retrieve_documents(
    query: str,
    top_k: int = 5
) -> list[dict]:
    """
    Retrieve the most relevant documents from ChromaDB
    for the given user query.
    """

    if not query.strip():
        return []

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved_documents = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        retrieved_documents.append({
            "text": document,
            "metadata": metadata,
            "distance": distance,
        })

    return retrieved_documents