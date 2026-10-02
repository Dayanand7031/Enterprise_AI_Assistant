from typing import TypedDict


class ChatState(TypedDict, total=False):
    query: str
    history: list[dict]

    # Authenticated user
    user_id: int


    # Planner
    planner_route: str
    planner_reason: str

    # RAG
    retrieval_query: str
    retrieved_documents: list[dict]
    relevant_documents: list[dict]
    retrieval_relevant: bool
    evaluation_reason: str

    # Retry
    retry_count: int
    max_retries: int

    # Final response
    answer: str
    sources: list[dict]