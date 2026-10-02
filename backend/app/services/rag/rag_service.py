from app.services.llm_service import generate_response
from app.services.rag.retrieval_service import retrieve_documents
from app.services.query_rewrite_service import rewrite_query

DEFAULT_TOP_K = 5
DEFAULT_MAX_DISTANCE = 1.10


def build_context(documents: list[dict]) -> str:
    context_parts = []

    for index, document in enumerate(documents, start=1):
        metadata = document["metadata"]

        filename = metadata.get("filename", "Unknown document")
        page = metadata.get("page", "Unknown")
        content_type = metadata.get("content_type", "unknown")

        context_parts.append(
            f"""
            SOURCE {index}
            File: {filename}
            Page: {page}
            Content Type: {content_type}

            {document["text"]}
            """.strip()
        )

    return "\n\n".join(context_parts)


def build_conversation_history(history: list[dict]) -> str:
    if not history:
        return "No previous conversation."

    history_parts = []

    for message in history:
        role = message["role"].upper()
        content = message["content"]

        history_parts.append(
            f"{role}: {content}"
        )

    return "\n".join(history_parts)


def filter_relevant_documents(
    documents: list[dict],
    max_distance: float = DEFAULT_MAX_DISTANCE
) -> list[dict]:

    return [
        document
        for document in documents
        if document["distance"] <= max_distance
    ]


def generate_rag_response(
    query: str,
    history: list[dict] | None = None,
    top_k: int = DEFAULT_TOP_K,
    max_distance: float = DEFAULT_MAX_DISTANCE
) -> dict:

    history = history or []

    retrieval_query = rewrite_query(
        query=query,
        history=history
    )
    print(f"Original query: {query}")
    print(f"Retrieval query: {retrieval_query}")

    retrieved_documents = retrieve_documents(
        retrieval_query,
        top_k=top_k
    )

    relevant_documents = filter_relevant_documents(
        retrieved_documents,
        max_distance=max_distance
    )

    if not relevant_documents:
        return {
            "answer": "I could not find relevant information in the company documents.",
            "sources": [],
        }

    context = build_context(relevant_documents)

    conversation_history = build_conversation_history(history)

    prompt = f"""
        You are an enterprise AI assistant.

        Answer the user's question using ONLY the provided
        company document context.

        You may use the conversation history to understand
        what the user is referring to.

        If the answer cannot be found in the company documents,
        say that the information is not available in the
        provided company documents.

        Do not invent or assume information.

        Keep the answer concise and directly answer the user's
        question.

        CONVERSATION HISTORY:
        {conversation_history}

        CURRENT USER QUESTION:
        {query}

        COMPANY DOCUMENT CONTEXT:
        {context}
        """

    answer = generate_response(prompt)

    sources = []

    for document in relevant_documents:
        metadata = document["metadata"]

        sources.append({
            "filename": metadata.get("filename"),
            "page": metadata.get("page"),
            "content_type": metadata.get("content_type"),
            "table_type": metadata.get("table_type"),
            "distance": document["distance"],
        })

    return {
        "answer": answer,
        "sources": sources,
    }