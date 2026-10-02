from app.graph.state import ChatState
from app.services.query_rewrite_service import rewrite_query
from app.services.rag.retrieval_service import retrieve_documents
from app.services.rag.rag_service import (
    build_context,
    build_conversation_history,
    filter_relevant_documents,
)

from app.db.database import SessionLocal
from app.models.auth_model import User

from app.services.mcp.mcp_authorization import (
    authorize_mcp_tool,
    MCPAuthorizationError,
)


from app.services.mcp.mcp_service import (
    create_enterprise_ticket,
    get_enterprise_ticket,
    get_enterprise_tickets,
    update_enterprise_ticket,

    jira_cloud_create_enterprise_ticket,
    jira_cloud_get_enterprise_ticket,
    jira_cloud_list_enterprise_tickets,
    jira_cloud_update_enterprise_ticket,
)


from app.services.capability_service import (
    get_capabilities_response,
)

from app.services.query_classifier import (
    is_greeting,
    get_greeting_response,
)


from app.services.mcp.mcp_planner_service import plan_mcp_action

from app.services.llm_service import generate_response
from app.services.evaluation_service import (
    evaluate_retrieval as evaluate_retrieval_service
)
from app.services.planner_service import plan_query


def prepare_query(state: ChatState) -> ChatState:
    query = state["query"]
    history = state.get("history", [])

    retrieval_query = rewrite_query(
        query=query,
        history=history
    )

    return {
        "retrieval_query": retrieval_query
    }


def retrieve(state: ChatState) -> ChatState:
    retrieval_query = state["retrieval_query"]

    retrieved_documents = retrieve_documents(
        retrieval_query,
        top_k=5
    )

    relevant_documents = filter_relevant_documents(
        retrieved_documents,
        max_distance=1.10
    )

    return {
        "retrieved_documents": retrieved_documents,
        "relevant_documents": relevant_documents
    }


def generate(state: ChatState) -> ChatState:
    query = state["query"]
    history = state.get("history", [])
    relevant_documents = state.get("relevant_documents", [])

    if not relevant_documents:
        return {
            "answer": (
                "I could not find relevant information "
                "in the company documents."
            ),
            "sources": []
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

Keep the answer concise and directly answer the
user's question.

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
        "sources": sources
    }



def fallback(state: ChatState) -> ChatState:
    return {
        "answer": (
            "I could not find relevant information "
            "in the company documents."
        ),
        "sources": []
    }


def evaluate_retrieval(state: ChatState) -> ChatState:
    relevant_documents = state.get(
        "relevant_documents",
        []
    )

    is_relevant = len(relevant_documents) > 0

    return {
        "retrieval_relevant": is_relevant
    }


def evaluate_retrieval_node(state: ChatState) -> ChatState:

    query = state["query"]

    relevant_documents = state.get(
        "relevant_documents",
        []
    )

    evaluation = evaluate_retrieval_service(
        query=query,
        documents=relevant_documents
    )

    return {
        "retrieval_relevant": evaluation["relevant"],
        "evaluation_reason": evaluation["reason"]
    }

def route_after_evaluation(state: ChatState) -> str:

    if state.get("retrieval_relevant", False):
        return "generate"

    retry_count = state.get(
        "retry_count",
        0
    )

    max_retries = state.get(
        "max_retries",
        1
    )

    if retry_count < max_retries:
        return "retry"

    return "fallback"


def retry_query(state: ChatState) -> ChatState:

    query = state["query"]
    history = state.get("history", [])
    current_retrieval_query = state.get(
        "retrieval_query",
        query
    )

    retry_count = state.get(
        "retry_count",
        0
    )

    conversation = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in history
    )

    prompt = f"""
You are a search query improvement component for an
enterprise RAG system.

The previous retrieval attempt did not find enough
relevant information.

Rewrite the retrieval query to improve document
retrieval.

ORIGINAL USER QUESTION:
{query}

PREVIOUS RETRIEVAL QUERY:
{current_retrieval_query}

CONVERSATION HISTORY:
{conversation if conversation else "No previous conversation."}

RULES:

1. Preserve the user's original intent.

2. Use conversation history to resolve references.

3. Include important entities and terminology that are
   supported by the conversation.

4. Do not introduce unsupported facts.

5. Do not answer the question.

6. Return ONLY the improved standalone search query.
"""

    improved_query = generate_response(prompt).strip()

    return {
        "retrieval_query": improved_query,
        "retry_count": retry_count + 1
    }


def planner(state: ChatState) -> ChatState:
    query = state["query"].strip()
    history = state.get("history", [])

    # =====================================================
    # 1. GREETING
    # =====================================================

    if is_greeting(query):
        return {
            "planner_route": "GREETING",
            "planner_reason": "User greeting detected."
        }

    # =====================================================
    # 2. CAPABILITY QUESTION
    # =====================================================

    normalized = query.lower()

    capability_phrases = [
        "what can you do",
        "what can you help me with",
        "what are your capabilities",
        "what features do you have",
        "what can you help with",
    ]

    if any(
        phrase in normalized
        for phrase in capability_phrases
    ):
        return {
            "planner_route": "CAPABILITIES",
            "planner_reason": "User asked about assistant capabilities."
        }

    # =====================================================
    # 3. EXISTING LLM PLANNER
    # =====================================================

    result = plan_query(
        query=query,
        history=history
    )

    return {
        "planner_route": result["route"],
        "planner_reason": result["reason"]
    }

def route_after_planner(state: ChatState) -> str:

    route = state.get("planner_route", "RAG")

    if route == "GREETING":
        return "greeting"

    if route == "CAPABILITIES":
        return "capabilities"

    if route == "MCP":
        return "mcp"

    if route == "CREWAI":
        return "crewai"

    return "rag"


def greeting_node(state: ChatState) -> ChatState:
    return {
        "answer": get_greeting_response(),
        "sources": []
    }


def capabilities_node(state: ChatState) -> ChatState:
    return {
        "answer": get_capabilities_response(),
        "sources": []
    }
# def mcp_placeholder(state: ChatState) -> ChatState:

#     return {
#         "answer": (
#             "MCP capability selected. "
#             "MCP integration will be implemented next."
#         ),
#         "sources": []
#     }


def crewai_placeholder(state: ChatState) -> ChatState:

    return {
        "answer": (
            "CrewAI capability selected. "
            "CrewAI integration will be implemented next."
        ),
        "sources": []
    }



async def mcp_node(state: ChatState):
    query = state["query"]
    history = state.get("history", [])
    user_id = state["user_id"]

    # -----------------------------------------
    # Ask LLM which MCP tool to execute
    # -----------------------------------------
    plan = plan_mcp_action(
        query=query,
        history=history
    )

    if not plan.get("success"):
        return {
            "answer": plan.get(
                "error",
                "I could not understand the requested MCP action."
            ),
            "sources": []
        }

    tool = plan["tool"]
    arguments = plan.get("arguments", {})

    print("========== MCP DEBUG ==========")
    print("user_id:", user_id)
    print("tool:", tool)
    print("arguments:", arguments)
    print("===============================")

    # -----------------------------------------
    # MCP AUTHORIZATION
    # -----------------------------------------

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            return {
                "answer": "User not found.",
                "sources": [],
            }

        authorize_mcp_tool(
            db=db,
            user=user,
            tool_name=tool,
        )

    except MCPAuthorizationError as exc:
        return {
            "answer": str(exc),
            "sources": [],
        }

    finally:
        db.close()

    # -----------------------------------------
    # CREATE TICKET
    # -----------------------------------------
    if tool == "create_ticket":

        title = arguments.get("title")
        description = arguments.get("description")
        priority = arguments.get("priority", "medium")

        if not title or not description:
            return {
                "answer": "Ticket title and description are required.",
                "sources": []
            }

        result = await create_enterprise_ticket(
            title=title,
            description=description,
            priority=priority,
            user_id=user_id
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to create the ticket."
                ),
                "sources": []
            }

        ticket = result["ticket"]

        answer = (
            f"Jira ticket created successfully.\n\n"
            f"Ticket ID: {ticket['id']}\n"
            f"Title: {ticket['title']}\n"
            f"Priority: {ticket['priority']}\n"
            f"Status: {ticket['status']}"
        )

        return {
            "answer": answer,
            "sources": []
        }


    # -----------------------------------------
    # JIRA CLOUD CREATE TICKET
    # -----------------------------------------
    if tool == "jira_cloud_create_ticket":

        project_key = arguments.get("project_key")
        title = arguments.get("title")
        description = arguments.get("description")
        issue_type = arguments.get("issue_type", "Task")

        if not project_key:
            return {
                "answer": "Jira project key is required.",
                "sources": []
            }

        if not title or not description:
            return {
                "answer": (
                    "Jira issue title and description "
                    "are required."
                ),
                "sources": []
            }

        result = await jira_cloud_create_enterprise_ticket(
            project_key=project_key,
            title=title,
            description=description,
            issue_type=issue_type,
            user_id=user_id,
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to create the Jira Cloud issue."
                ),
                "sources": []
            }

        issue = result.get("issue", {})

        answer = (
            "Jira Cloud issue created successfully.\n\n"
            f"Issue Key: {issue.get('key', 'N/A')}\n"
            f"Issue ID: {issue.get('id', 'N/A')}\n"
            f"Title: {title}\n"
            f"Project: {project_key.upper()}\n"
            f"Issue Type: {issue_type}"
        )

        return {
            "answer": answer,
            "sources": []
        }

    # -----------------------------------------
    # GET TICKET
    # -----------------------------------------
    if tool == "get_ticket":

        ticket_id = arguments.get("ticket_id")

        if ticket_id is None:
            return {
                "answer": "Ticket ID is required.",
                "sources": []
            }

        try:
            ticket_id = int(ticket_id)
        except (TypeError, ValueError):
            return {
                "answer": "Invalid ticket ID.",
                "sources": []
            }

        result = await get_enterprise_ticket(
            ticket_id=ticket_id,
            user_id=user_id
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to retrieve the ticket."
                ),
                "sources": []
            }

        ticket = result["ticket"]

        answer = (
            f"Jira ticket #{ticket['id']}\n\n"
            f"Title: {ticket['title']}\n"
            f"Description: {ticket['description']}\n"
            f"Priority: {ticket['priority']}\n"
            f"Status: {ticket['status']}\n"
            f"Created By: {ticket['created_by']}"
        )

        return {
            "answer": answer,
            "sources": []
        }

    # -----------------------------------------
    # JIRA CLOUD GET TICKET
    # -----------------------------------------
    if tool == "jira_cloud_get_ticket":

        issue_key = arguments.get("issue_key")

        if not issue_key:
            return {
                "answer": "Jira issue key is required.",
                "sources": []
            }

        result = await jira_cloud_get_enterprise_ticket(
            issue_key=issue_key,
            user_id=user_id,
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to retrieve the Jira Cloud issue."
                ),
                "sources": []
            }

        issue = result.get("issue", {})

        fields = issue.get("fields", {})

        summary = fields.get("summary", "N/A")

        status = fields.get(
            "status",
            {}
        )

        status_name = (
            status.get("name", "N/A")
            if isinstance(status, dict) 
            else "N/A"
        )

        issue_type = fields.get(
            "issuetype",
            {}
        )

        issue_type_name = (
            issue_type.get("name", "N/A")
            if isinstance(issue_type, dict)
            else "N/A"
        )

        answer = (
            f"Jira Cloud issue {issue_key.upper()}\n\n"
            f"Summary: {summary}\n"
            f"Status: {status_name}\n"
            f"Issue Type: {issue_type_name}\n"
            f"Issue ID: {issue.get('id', 'N/A')}"
        )

        return {
            "answer": answer,
            "sources": []
        }

    # -----------------------------------------
    # LIST TICKETS
    # -----------------------------------------
    if tool == "list_tickets":

        result = await get_enterprise_tickets(
            user_id=user_id
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to retrieve the Jira tickets."
                ),
                "sources": []
            }

        tickets = result.get("tickets", [])

        if not tickets:
            return {
                "answer": "There are currently no Jira tickets.",
                "sources": []
            }

        lines = [
            f"Found {len(tickets)} Jira ticket(s):\n"
        ]

        for ticket in tickets:
            lines.append(
                f"#{ticket['id']} - "
                f"{ticket['title']} | "
                f"Priority: {ticket['priority']} | "
                f"Status: {ticket['status']}"
            )

        return {
            "answer": "\n".join(lines),
            "sources": []
        }



    # -----------------------------------------
    # JIRA CLOUD LIST TICKETS
    # -----------------------------------------
    if tool == "jira_cloud_list_tickets":

        jql = arguments.get("jql")

        max_results = arguments.get(
            "max_results",
            20
        )

        if not jql:
            return {
                "answer": "JQL query is required.",
                "sources": []
            }

        try:
            max_results = int(max_results)
        except (TypeError, ValueError):
            return {
                "answer": "Invalid max_results value.",
                "sources": []
            }

        result = await jira_cloud_list_enterprise_tickets(
            jql=jql,
            max_results=max_results,
            user_id=user_id,
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to search Jira Cloud issues."
                ),
                "sources": []
            }

        issue_data = result.get(
            "issues",
            {}
        )

        issues = issue_data.get(
            "issues",
            []
        )

        if not issues:
            return {
                "answer": "No Jira Cloud issues were found.",
                "sources": []
            }

        lines = [
            f"Found {len(issues)} Jira Cloud issue(s):\n"
        ]

        for issue in issues:

            key = issue.get(
                "key",
                "N/A"
            )

            fields = issue.get(
                "fields",
                {}
            )

            summary = fields.get(
                "summary",
                "N/A"
            )

            status = fields.get(
                "status",
                {}
            )

            status_name = (
                status.get("name", "N/A")
                if isinstance(status, dict)
                else "N/A"
            )

            lines.append(
                f"{key} - "
                f"{summary} | "
                f"Status: {status_name}"
            )

        return {
            "answer": "\n".join(lines),
            "sources": []
        }
    # -----------------------------------------
    # UPDATE TICKET
    # -----------------------------------------
    if tool == "update_ticket":

        ticket_id = arguments.get("ticket_id")

        if ticket_id is None:
            return {
                "answer": "Ticket ID is required.",
                "sources": []
            }

        try:
            ticket_id = int(ticket_id)
        except (TypeError, ValueError):
            return {
                "answer": "Invalid ticket ID.",
                "sources": []
            }

        result = await update_enterprise_ticket(
            ticket_id=ticket_id,
            user_id=user_id,
            title=arguments.get("title"),
            description=arguments.get("description"),
            priority=arguments.get("priority"),
            status=arguments.get("status"),
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to update the ticket."
                ),
                "sources": []
            }

        ticket = result["ticket"]

        answer = (
            f"Jira ticket #{ticket['id']} updated successfully.\n\n"
            f"Title: {ticket['title']}\n"
            f"Priority: {ticket['priority']}\n"
            f"Status: {ticket['status']}"
        )

        return {
            "answer": answer,
            "sources": []
        }

    
    
    # -----------------------------------------
    # JIRA CLOUD UPDATE TICKET
    # -----------------------------------------
    if tool == "jira_cloud_update_ticket":

        issue_key = arguments.get(
            "issue_key"
        )

        title = arguments.get(
            "title"
        )

        description = arguments.get(
            "description"
        )

        if not issue_key:
            return {
                "answer": "Jira issue key is required.",
                "sources": []
            }

        if title is None and description is None:
            return {
                "answer": (
                    "At least one field is required "
                    "for Jira issue update."
                ),
                "sources": []
            }

        result = await jira_cloud_update_enterprise_ticket(
            issue_key=issue_key,
            user_id=user_id,
            title=title,
            description=description,
        )

        if not result.get("success"):
            return {
                "answer": result.get(
                    "error",
                    "I was unable to update the Jira Cloud issue."
                ),
                "sources": []
            }

        answer = (
            f"Jira Cloud issue "
            f"{issue_key.upper()} "
            f"updated successfully."
        )

        return {
            "answer": answer,
            "sources": []
        }

    # -----------------------------------------
    # UNKNOWN TOOL
    # -----------------------------------------
    return {
        "answer": (
            f"The MCP tool '{tool}' is recognized by the planner, "
            f"but it is not implemented in the current system."
        ),
        "sources": []
    }