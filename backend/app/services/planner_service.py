from app.services.llm_service import generate_response
import json


def plan_query(query: str, history: list[dict] | None = None) -> dict:
    history = history or []

    conversation = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in history
    )

    if not conversation:
        conversation = "No previous conversation."

    prompt = f"""
You are the planner component of an enterprise AI assistant.

Your job is to determine which capability should handle the
user's request.

Available capabilities:

1. RAG
   Use RAG when the user is asking about information contained
   in company documents, policies, manuals, procedures,
   guidelines, leave policies, holiday calendars, or other
   internal knowledge.

2. MCP
   Use MCP when the request requires interacting with an
   external system or enterprise tool.

   Examples:
   - Create a Jira ticket
   - Check Jira issue status
   - Get employee information from an HR system
   - Query an external business system
   - Update a record
   - Perform an action using an enterprise tool

3. CREWAI
   Use CREWAI when the request requires multi-agent research,
   complex analysis, investigation, comparison, or combining
   multiple specialized reasoning tasks.

   Examples:
   - Research a complex business topic
   - Compare multiple technical approaches
   - Perform a multi-step investigation
   - Analyze information from multiple sources

RULES:

1. Choose exactly ONE capability.

2. Return "RAG", "MCP", or "CREWAI".

3. Use the conversation history to understand the current request.

4. Do not answer the user's question.

5. Do not invent information.

6. Return ONLY valid JSON.

Use exactly this format:

{{
    "route": "RAG",
    "reason": "The request asks for information from company documents."
}}

or:

{{
    "route": "MCP",
    "reason": "The request requires interaction with an enterprise tool."
}}

or:

{{
    "route": "CREWAI",
    "reason": "The request requires multi-agent research or complex analysis."
}}

CONVERSATION HISTORY:
{conversation}

CURRENT USER QUESTION:
{query}
"""

    response = generate_response(prompt).strip()

    try:
        result = json.loads(response)

    except json.JSONDecodeError:

        # Try to extract JSON if the LLM wrapped it
        # in markdown or additional text.
        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1 and end > start:

            try:
                result = json.loads(
                    response[start:end + 1]
                )

            except json.JSONDecodeError:

                return {
                    "route": "RAG",
                    "reason": (
                        "Unable to parse planner response; "
                        "defaulting to RAG."
                    )
                }

        else:

            return {
                "route": "RAG",
                "reason": (
                    "Unable to parse planner response; "
                    "defaulting to RAG."
                )
            }


    route = str(
        result.get("route", "")
    ).strip().upper()

    reason = str(
        result.get("reason", "")
    ).strip()


    if route not in {"RAG", "MCP", "CREWAI"}:

        return {
            "route": "RAG",
            "reason": (
                "Invalid planner route; "
                "defaulting to RAG."
            )
        }


    return {
        "route": route,
        "reason": reason
    }