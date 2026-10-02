from app.services.llm_service import generate_response


def evaluate_retrieval(
    query: str,
    documents: list[dict]
) -> dict:

    if not documents:
        return {
            "relevant": False,
            "reason": "No relevant documents were retrieved."
        }

    context_parts = []

    for index, document in enumerate(documents, start=1):
        metadata = document.get("metadata", {})

        context_parts.append(
            f"""
    DOCUMENT {index}

    File: {metadata.get("filename", "Unknown")}
    Page: {metadata.get("page", "Unknown")}
    Content Type: {metadata.get("content_type", "Unknown")}
    Table Type: {metadata.get("table_type", "Unknown")}

    Document Content:
    {document["text"]}
    """.strip()
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a retrieval evaluation component in an enterprise RAG system.

Your job is to determine whether the retrieved company document
context contains enough information to answer the user's question.

USER QUESTION:
{query}

RETRIEVED DOCUMENT CONTEXT:
{context}

EVALUATION RULES:

1. Evaluate both the document CONTENT and its METADATA.

2. A document is relevant if it contains enough information to
   answer the user's question directly OR allows the answer to be
   reliably inferred from the document's structure and metadata.

3. Pay attention to metadata such as:
   - table_type
   - content_type
   - page
   - filename
   - document section
   - category

4. If the question asks whether a particular date or event is a
   company holiday, and the retrieved document is a
   "holiday_calendar" table containing that holiday and date,
   consider the document relevant.

5. Do not require the exact wording of the user's question to
   appear in the document.

6. Mark relevant as false only when the retrieved documents are
   unrelated or genuinely lack enough information to answer.

7. Do not use outside knowledge.

8. Do not answer the user's question.

9. Return ONLY valid JSON.

Use exactly this format:

{{
    "relevant": true,
    "reason": "short explanation"
}}
"""

    response = generate_response(prompt)

    # Temporary parsing approach.
    # We will make this more robust later.
    import json

    try:
        result = json.loads(response)

        return {
            "relevant": bool(result.get("relevant", False)),
            "reason": str(result.get("reason", ""))
        }

    except (json.JSONDecodeError, TypeError, ValueError):
        return {
            "relevant": False,
            "reason": "Unable to parse retrieval evaluation."
        }