import json

from app.services.llm_service import generate_response


ALLOWED_TOOLS = {
    # Local PostgreSQL MCP tools
    "create_ticket",
    "get_ticket",
    "list_tickets",
    "update_ticket",

    # Jira Cloud MCP tools
    "jira_cloud_create_ticket",
    "jira_cloud_get_ticket",
    "jira_cloud_list_tickets",
    "jira_cloud_update_ticket",
}


def plan_mcp_action(
    query: str,
    history: list[dict] | None = None,
) -> dict:

    history = history or []

    conversation = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in history
    )

    if not conversation:
        conversation = "No previous conversation."

    prompt = f"""
You are the MCP planning component of an enterprise AI assistant.

Your job is to determine which MCP tool should be used and
extract the parameters required by that tool.

There are TWO ticket systems available:

1. LOCAL MCP TICKET SYSTEM
2. JIRA CLOUD MCP TICKET SYSTEM


==================================================
LOCAL MCP TOOLS
==================================================

1. create_ticket

Creates a ticket in the local enterprise ticket system.

Parameters:

- title: short ticket title
- description: detailed description
- priority: one of "low", "medium", "high", "critical"


2. get_ticket

Retrieves a ticket from the local ticket system.

Parameters:

- ticket_id: numeric ticket identifier


3. list_tickets

Lists tickets from the local ticket system.

Parameters:

- no parameters required


4. update_ticket

Updates a local ticket.

Parameters:

- ticket_id: numeric ticket identifier
- title: optional new title
- description: optional new description
- priority: optional "low", "medium", "high", or "critical"
- status: optional "open", "in_progress", "resolved", or "closed"


==================================================
JIRA CLOUD MCP TOOLS
==================================================

5. jira_cloud_create_ticket

Creates a real Jira Cloud issue.

Parameters:

- project_key: Jira project key such as "KAN"
- title: short issue title
- description: detailed issue description
- issue_type: Jira issue type such as "Task", "Bug", or "Story"


6. jira_cloud_get_ticket

Retrieves a Jira Cloud issue.

Parameters:

- issue_key: Jira issue key such as "KAN-5"


7. jira_cloud_list_tickets

Searches Jira Cloud issues using JQL.

Parameters:

- jql: Jira Query Language query
- max_results: maximum number of issues to return

Default max_results is 20.


8. jira_cloud_update_ticket

Updates a Jira Cloud issue.

Parameters:

- issue_key: Jira issue key such as "KAN-5"
- title: optional new title
- description: optional new description


==================================================
TOOL SELECTION RULES
==================================================

1. Choose exactly ONE MCP tool.

2. Use Jira Cloud MCP tools when the user:

   - explicitly mentions Jira Cloud
   - mentions Atlassian
   - provides a Jira issue key such as KAN-5
   - provides a Jira project key such as KAN
   - mentions JQL
   - explicitly asks to create, search, retrieve, or update
     a Jira issue


3. If the user provides a Jira issue key such as:

   KAN-5
   PROJ-123
   DEMO-1001

   treat it as a Jira Cloud issue key.

   - If the user asks to view, get, retrieve, check,
     inspect, or show the issue:
     use jira_cloud_get_ticket.

   - If the user asks to update, change, modify, rename,
     or edit the issue:
     use jira_cloud_update_ticket.


4. If the user asks to CREATE a Jira Cloud issue
   and provides a project key, use:

   jira_cloud_create_ticket.


5. If the user asks to SEARCH, FIND, or LIST
   multiple Jira Cloud issues, use:

   jira_cloud_list_tickets.

   If the user asks about one specific issue key,
   use jira_cloud_get_ticket or
   jira_cloud_update_ticket according to the request.


6. For Jira Cloud searches, create a valid JQL query
   based only on information provided by the user.


7. Do not invent Jira issue keys.

8. Do not invent project keys.

9. Do not invent ticket IDs.

10. Do not invent facts about the issue.


11. If the user does not identify Jira Cloud,
    does not provide a Jira issue key or project key,
    and asks for a generic "ticket",
    use the LOCAL MCP ticket tools.


12. For local ticket creation:

    - Create a concise title.
    - Preserve the user's actual issue in the description.
    - If priority is explicitly specified, use it.
    - Otherwise use "medium".


13. For Jira Cloud ticket creation:

    - Extract the project_key from the request.
    - Create a concise title.
    - Preserve the user's actual issue in the description.
    - If issue_type is not specified, use "Task".


14. For updates:

    - Only include fields that the user actually wants
      to update.
    - Do not invent missing values.


15. Return ONLY valid JSON.


==================================================
EXAMPLES
==================================================

LOCAL CREATE:

{{
    "tool": "create_ticket",
    "arguments": {{
        "title": "Login API returning 500 errors",
        "description": "The login API is returning 500 errors.",
        "priority": "high"
    }}
}}


LOCAL GET:

{{
    "tool": "get_ticket",
    "arguments": {{
        "ticket_id": 6
    }}
}}


LOCAL LIST:

{{
    "tool": "list_tickets",
    "arguments": {{}}
}}


LOCAL UPDATE:

{{
    "tool": "update_ticket",
    "arguments": {{
        "ticket_id": 6,
        "priority": "high"
    }}
}}


JIRA CLOUD CREATE:

{{
    "tool": "jira_cloud_create_ticket",
    "arguments": {{
        "project_key": "KAN",
        "title": "Login API returning 500 errors",
        "description": "The login API is returning 500 errors.",
        "issue_type": "Bug"
    }}
}}


JIRA CLOUD GET:

{{
    "tool": "jira_cloud_get_ticket",
    "arguments": {{
        "issue_key": "KAN-5"
    }}
}}


JIRA CLOUD LIST:

{{
    "tool": "jira_cloud_list_tickets",
    "arguments": {{
        "jql": "project = KAN ORDER BY created DESC",
        "max_results": 20
    }}
}}


JIRA CLOUD UPDATE:

{{
    "tool": "jira_cloud_update_ticket",
    "arguments": {{
        "issue_key": "KAN-5",
        "title": "Updated Jira issue title"
    }}
}}


==================================================
CONVERSATION HISTORY
==================================================

{conversation}


==================================================
CURRENT USER REQUEST
==================================================

{query}
"""

    response = generate_response(prompt).strip()

    # ---------------------------------------------
    # Parse JSON
    # ---------------------------------------------

    try:

        result = json.loads(response)

    except json.JSONDecodeError:

        start = response.find("{")
        end = response.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return {
                "success": False,
                "error": "Unable to parse MCP planner response.",
            }

        try:

            result = json.loads(
                response[start:end + 1]
            )

        except json.JSONDecodeError:

            return {
                "success": False,
                "error": "Unable to parse MCP planner response.",
            }

    # ---------------------------------------------
    # Validate tool
    # ---------------------------------------------

    tool = str(
        result.get("tool", "")
    ).strip()

    if tool not in ALLOWED_TOOLS:

        return {
            "success": False,
            "error": f"Unsupported MCP tool: {tool}",
        }

    # ---------------------------------------------
    # Validate arguments
    # ---------------------------------------------

    arguments = result.get("arguments")

    if not isinstance(arguments, dict):

        return {
            "success": False,
            "error": "MCP planner returned invalid arguments.",
        }

    return {
        "success": True,
        "tool": tool,
        "arguments": arguments,
    }