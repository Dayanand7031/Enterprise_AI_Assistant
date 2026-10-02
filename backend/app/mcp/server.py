from mcp.server import MCPServer

from app.db.database import SessionLocal
from app.schemas.jira import JiraTicketCreate

from app.services.jira_integrations.postgres_jira.jira_service import (
    create_ticket as create_jira_ticket,
    get_ticket as get_jira_ticket,
    list_tickets as list_jira_tickets,
    update_ticket as update_jira_ticket,
)

from app.services.jira_integrations.jira_cloud.jira_client import (
    JiraClient,
)


from app.services.jira_integrations.jira_cloud.jira_client import (
    JiraClient,
)

from app.schemas.jira import (
    JiraTicketCreate,
    JiraTicketUpdate,
)

mcp = MCPServer("Enterprise Ticket Server")


@mcp.tool()
def create_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    created_by: int | None = None,
) -> dict:

    # ---------------------------------------------
    # Validate priority
    # ---------------------------------------------

    allowed_priorities = {
        "low",
        "medium",
        "high",
        "critical",
    }

    normalized_priority = priority.lower().strip()

    if normalized_priority not in allowed_priorities:
        return {
            "success": False,
            "error": (
                f"Invalid priority '{priority}'. "
                f"Allowed values: "
                f"{', '.join(sorted(allowed_priorities))}"
            ),
        }

    # ---------------------------------------------
    # Validate title
    # ---------------------------------------------

    if not title.strip():
        return {
            "success": False,
            "error": "Ticket title cannot be empty.",
        }

    # ---------------------------------------------
    # Validate description
    # ---------------------------------------------

    if not description.strip():
        return {
            "success": False,
            "error": "Ticket description cannot be empty.",
        }

    # ---------------------------------------------
    # Validate authenticated user
    # ---------------------------------------------

    if created_by is None:
        return {
            "success": False,
            "error": "Authenticated user is required.",
        }

    db = SessionLocal()

    try:

        # -----------------------------------------
        # Build Jira schema
        # -----------------------------------------

        ticket_data = JiraTicketCreate(
            title=title.strip(),
            description=description.strip(),
            priority=normalized_priority,
        )

        # -----------------------------------------
        # Create actual database ticket
        # -----------------------------------------

        ticket = create_jira_ticket(
            db=db,
            ticket_data=ticket_data,
            created_by=created_by,
        )

        # -----------------------------------------
        # Return serialized result
        # -----------------------------------------

        return {
            "success": True,
            "ticket": {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_by": ticket.created_by,
                "created_at": (
                    ticket.created_at.isoformat()
                    if ticket.created_at
                    else None
                ),
            },
        }

    except Exception as exc:

        db.rollback()

        return {
            "success": False,
            "error": f"Unable to create ticket: {str(exc)}",
        }

    finally:
        db.close()



@mcp.tool()
async def jira_cloud_create_ticket(
    user_id: int,
    project_key: str,
    title: str,
    description: str,
    issue_type: str = "Task",
) -> dict:
    """
    Create an issue in Jira Cloud.
    """

    # ---------------------------------------------
    # Validate user
    # ---------------------------------------------

    if user_id is None:
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "Authenticated user is required.",
        }

    # ---------------------------------------------
    # Validate project
    # ---------------------------------------------

    if not project_key.strip():
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "Jira project key cannot be empty.",
        }

    # ---------------------------------------------
    # Validate title
    # ---------------------------------------------

    if not title.strip():
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "Issue title cannot be empty.",
        }

    # ---------------------------------------------
    # Validate description
    # ---------------------------------------------

    if not description.strip():
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "Issue description cannot be empty.",
        }

    db = SessionLocal()

    try:

        client = JiraClient(
            db=db,
            user_id=user_id,
        )

        issue = await client.create_issue(
            project_key=project_key.strip().upper(),
            summary=title.strip(),
            description=description.strip(),
            issue_type=issue_type.strip(),
        )

        return {
            "success": True,
            "source": "jira_cloud",
            "message": "Jira issue created successfully.",
            "issue": issue,
        }

    except Exception as exc:

        db.rollback()

        return {
            "success": False,
            "source": "jira_cloud",
            "error": f"Unable to create Jira issue: {str(exc)}",
        }

    finally:
        db.close()


@mcp.tool()
def get_ticket(ticket_id: int) -> dict:

    db = SessionLocal()

    try:

        ticket = get_jira_ticket(
            db=db,
            ticket_id=ticket_id,
        )

        if ticket is None:
            return {
                "success": False,
                "error": f"Ticket {ticket_id} not found.",
            }

        return {
            "success": True,
            "ticket": {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_by": ticket.created_by,
                "created_at": (
                    ticket.created_at.isoformat()
                    if ticket.created_at
                    else None
                ),
            },
        }

    except Exception as exc:

        db.rollback()

        return {
            "success": False,
            "error": f"Unable to retrieve ticket: {str(exc)}",
        }

    finally:
        db.close()



@mcp.tool()
async def jira_cloud_get_ticket(
    user_id: int,
    issue_key: str,
) -> dict:

    if not issue_key.strip():
        return {
            "success": False,
            "error": "Jira issue key cannot be empty.",
        }

    db = SessionLocal()

    try:

        client = JiraClient(
            db=db,
            user_id=user_id,
        )

        issue = await client.get_issue(
            issue_key=issue_key.strip().upper()
        )

        return {
            "success": True,
            "source": "jira_cloud",
            "issue": issue,
        }

    except Exception as exc:

        db.rollback()

        return {
            "success": False,
            "source": "jira_cloud",
            "error": f"Unable to retrieve Jira issue: {str(exc)}",
        }

    finally:
        db.close()




@mcp.tool()
def list_tickets() -> dict:

    db = SessionLocal()

    try:

        tickets = list_jira_tickets(
            db=db
        )

        result = []

        for ticket in tickets:

            result.append({
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_by": ticket.created_by,
                "created_at": (
                    ticket.created_at.isoformat()
                    if ticket.created_at
                    else None
                ),
            })

        return {
            "success": True,
            "tickets": result,
            "count": len(result),
        }

    except Exception as exc:

        return {
            "success": False,
            "error": f"Unable to list tickets: {str(exc)}",
        }

    finally:
        db.close()


@mcp.tool()
async def jira_cloud_list_tickets(
    user_id: int,
    jql: str,
    max_results: int = 20,
) -> dict:
    """
    Search Jira Cloud issues using JQL.
    """

    if not jql.strip():
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "JQL query cannot be empty.",
        }

    if max_results < 1 or max_results > 100:
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "max_results must be between 1 and 100.",
        }

    db = SessionLocal()

    try:
        client = JiraClient(
            db=db,
            user_id=user_id,
        )

        result = await client.get_issues(
            jql=jql.strip(),
            max_results=max_results,
        )

        return {
            "success": True,
            "source": "jira_cloud",
            "issues": result,
        }

    except Exception as exc:
        db.rollback()

        return {
            "success": False,
            "source": "jira_cloud",
            "error": f"Unable to search Jira issues: {str(exc)}",
        }

    finally:
        db.close()


@mcp.tool()
def update_ticket(
    ticket_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    status: str | None = None,
) -> dict:

    db = SessionLocal()

    try:

        # -----------------------------------------
        # Check ticket exists
        # -----------------------------------------

        ticket = get_jira_ticket(
            db=db,
            ticket_id=ticket_id,
        )

        if ticket is None:
            return {
                "success": False,
                "error": f"Ticket {ticket_id} not found.",
            }

        # -----------------------------------------
        # Build update payload
        # -----------------------------------------

        update_data = {}

        if title is not None:
            update_data["title"] = title

        if description is not None:
            update_data["description"] = description

        if priority is not None:
            update_data["priority"] = priority

        if status is not None:
            update_data["status"] = status

        if not update_data:
            return {
                "success": False,
                "error": "No fields provided for update.",
            }

        # -----------------------------------------
        # Validate update data
        # -----------------------------------------

        ticket_data = JiraTicketUpdate(
            **update_data
        )

        # -----------------------------------------
        # Update database
        # -----------------------------------------

        updated_ticket = update_jira_ticket(
            db=db,
            ticket_id=ticket_id,
            ticket_data=ticket_data,
        )

        if updated_ticket is None:
            return {
                "success": False,
                "error": f"Ticket {ticket_id} not found.",
            }

        # -----------------------------------------
        # Return updated ticket
        # -----------------------------------------

        return {
            "success": True,
            "ticket": {
                "id": updated_ticket.id,
                "title": updated_ticket.title,
                "description": updated_ticket.description,
                "priority": updated_ticket.priority,
                "status": updated_ticket.status,
                "created_by": updated_ticket.created_by,
                "created_at": (
                    updated_ticket.created_at.isoformat()
                    if updated_ticket.created_at
                    else None
                ),
            },
        }

    except Exception as exc:

        db.rollback()

        return {
            "success": False,
            "error": f"Unable to update ticket: {str(exc)}",
        }

    finally:
        db.close()

@mcp.tool()
async def jira_cloud_update_ticket(
    user_id: int,
    issue_key: str,
    title: str | None = None,
    description: str | None = None,
) -> dict:
    """
    Update an existing Jira Cloud issue.
    """

    if not issue_key.strip():
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "Jira issue key cannot be empty.",
        }

    if title is None and description is None:
        return {
            "success": False,
            "source": "jira_cloud",
            "error": "At least one field must be provided for update.",
        }

    db = SessionLocal()

    try:

        client = JiraClient(
            db=db,
            user_id=user_id,
        )

        result = await client.update_issue(
            issue_key=issue_key.strip().upper(),
            summary=title.strip() if title is not None else None,
            description=(
                description.strip()
                if description is not None
                else None
            ),
        )

        return {
            "success": True,
            "source": "jira_cloud",
            "message": "Jira issue updated successfully.",
            "issue": result,
        }

    except Exception as exc:

        db.rollback()

        return {
            "success": False,
            "source": "jira_cloud",
            "error": f"Unable to update Jira issue: {str(exc)}",
        }

    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()