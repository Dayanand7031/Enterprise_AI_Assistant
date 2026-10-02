from app.services.llm_service import generate_response


def rewrite_query(
    query: str,
    history: list[dict] | None = None
) -> str:
    history = history or []

    if not history:
        return query

    conversation = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in history
    )

    prompt = f"""
You are a query rewriting component in an enterprise RAG system.

Your job is to convert the user's current question into a
clear, standalone search query for retrieving relevant
information from company documents.

RULES:

1. Use the conversation history to resolve references such as:
   - "them", "it", "this", "that", "these", "those"
   - "the above", "the previous one", "the same"
   - pronouns or abbreviated terms whose meaning comes from
     the previous conversation.

2. Preserve the user's original intent.
   Do not change what the user is asking.

3. Make the query standalone.
   Someone reading ONLY the rewritten query should understand
   what information needs to be retrieved.

4. Include important entities and concepts from the conversation
   when they are necessary to understand the current question.

5. Do NOT introduce facts, entities, document names, policies,
   dates, numbers, or concepts that are not supported by the
   conversation.

6. Do NOT answer the user's question.

7. Do NOT add explanations, commentary, or formatting.

8. Return ONLY the standalone search query.

9. If the current question is already standalone, preserve it
   with only minimal rewriting when necessary.

CONVERSATION HISTORY:
{conversation}

CURRENT USER QUESTION:
{query}

STANDALONE SEARCH QUERY:
"""

    rewritten_query = generate_response(prompt)

    return rewritten_query.strip()