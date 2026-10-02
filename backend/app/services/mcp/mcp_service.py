import json
import time
from app.db.database import SessionLocal
from app.models.auth_model import User

from app.services.mcp.mcp_audit_service import create_mcp_audit_log
from app.services.mcp.mcp_client import create_ticket

from app.services.mcp.mcp_authorization import (
    authorize_mcp_tool,
    MCPAuthorizationError,
)
from app.services.mcp.mcp_audit_service import (
    audit_mcp_denial,
    audit_mcp_execution,
    get_execution_time_ms,
)
from app.services.mcp.mcp_response_service import (
    parse_mcp_response,
)

from app.services.mcp.mcp_client import (
    create_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
)


from app.services.jira_integrations.jira_cloud.jira_client import (
    JiraClient,
)


def get_authorized_user(
    user_id: int,
    tool_name: str,
):
    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return None, {
                "success": False,
                "error": "User not found.",
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name=tool_name,
            )

        except MCPAuthorizationError as exc:

            return None, {
                "success": False,
                "error": str(exc),
            }

        return user, None

    finally:
        db.close()




async def create_enterprise_ticket(
    title: str,
    description: str,
    priority: str = "medium",
    user_id: int | None = None,
) -> dict:

    # ---------------------------------------------
    # Validate authenticated user
    # ---------------------------------------------

    if user_id is None:
        return {
            "success": False,
            "error": "Authenticated user is required.",
        }

    arguments = {
        "title": title,
        "description": description,
        "priority": priority,
    }

    # ---------------------------------------------
    # Authentication + Authorization
    # ---------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="create_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="create_ticket",
            )

        except MCPAuthorizationError as exc:

            error = str(exc)

            # -----------------------------------------
            # Audit authorization failure
            # -----------------------------------------

            audit_mcp_denial(
                user_id=user_id,
                tool_name="create_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    # ---------------------------------------------
    # MCP execution
    # ---------------------------------------------

    start_time = time.perf_counter()

    try:

        result = await create_ticket(
            title=title,
            description=description,
            priority=priority,
            created_by=user_id,
        )

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        data = parse_mcp_response(result)

        # # -----------------------------------------
        # # MCP error
        # # -----------------------------------------

        # if result.is_error:

        #     error = "MCP tool execution failed."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="create_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # # -----------------------------------------
        # # Empty MCP response
        # # -----------------------------------------

        # if not result.content:

        #     error = "MCP server returned no content."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="create_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # first_content = result.content[0]

        # # -----------------------------------------
        # # Unexpected response format
        # # -----------------------------------------

        # if not hasattr(first_content, "text"):

        #     error = "Unexpected MCP response format."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="create_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # # -----------------------------------------
        # # Parse MCP response
        # # -----------------------------------------

        # try:

        #     data = json.loads(
        #         first_content.text
        #     )

        # except json.JSONDecodeError:

        #     error = "Unable to parse MCP tool response."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="create_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # -----------------------------------------
        # Audit actual MCP result
        # -----------------------------------------

        audit_mcp_execution(
            user_id=user_id,
            tool_name="create_ticket",
            arguments=arguments,
            success=data.get("success", False),
            result=data,
            error=data.get("error"),
            execution_time_ms=execution_time_ms,
        )

        return data

    # ---------------------------------------------
    # Unexpected execution exception
    # ---------------------------------------------

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        audit_mcp_execution(
            user_id=user_id,
            tool_name="create_ticket",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": str(exc),
        }


async def get_enterprise_ticket(
    ticket_id: int,
    user_id: int,
) -> dict:

    arguments = {
        "ticket_id": ticket_id,
    }

    # ---------------------------------------------
    # Authentication + Authorization
    # ---------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="get_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="get_ticket",
            )

        except MCPAuthorizationError as exc:

            error = str(exc)

            audit_mcp_denial(
                user_id=user_id,
                tool_name="get_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    # ---------------------------------------------
    # MCP execution
    # ---------------------------------------------

    start_time = time.perf_counter()

    try:

        result = await get_ticket(
            ticket_id=ticket_id
        )

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        data = parse_mcp_response(result)

        # -----------------------------------------
        # MCP error
        # -----------------------------------------

        # if result.is_error:

        #     error = "MCP tool execution failed."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="get_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # # -----------------------------------------
        # # Empty response
        # # -----------------------------------------

        # if not result.content:

        #     error = "MCP server returned no content."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="get_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # first_content = result.content[0]

        # # -----------------------------------------
        # # Response format validation
        # # -----------------------------------------

        # if not hasattr(first_content, "text"):

        #     error = "Unexpected MCP response format."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="get_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # # -----------------------------------------
        # # Parse response
        # # -----------------------------------------

        # try:

        #     data = json.loads(
        #         first_content.text
        #     )

        # except json.JSONDecodeError:

        #     error = "Unable to parse MCP tool response."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="get_ticket",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # -----------------------------------------
        # Audit MCP result
        # -----------------------------------------

        audit_mcp_execution(
            user_id=user_id,
            tool_name="get_ticket",
            arguments=arguments,
            success=data.get("success", False),
            result=data,
            error=data.get("error"),
            execution_time_ms=execution_time_ms,
        )

        return data

    # ---------------------------------------------
    # Unexpected exception
    # ---------------------------------------------

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        audit_mcp_execution(
            user_id=user_id,
            tool_name="get_ticket",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": str(exc),
        }


async def get_enterprise_tickets(
    user_id: int,
) -> dict:

    arguments = {}

    # ---------------------------------------------
    # Authentication + Authorization
    # ---------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="list_tickets",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="list_tickets",
            )

        except MCPAuthorizationError as exc:

            error = str(exc)

            audit_mcp_denial(
                user_id=user_id,
                tool_name="list_tickets",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    # ---------------------------------------------
    # MCP execution
    # ---------------------------------------------

    start_time = time.perf_counter()

    try:

        result = await list_tickets()

        execution_time_ms = get_execution_time_ms(
            start_time
        )
        data = parse_mcp_response(result)

        # -----------------------------------------
        # MCP error
        # -----------------------------------------

        # if result.is_error:

        #     error = "MCP tool execution failed."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="list_tickets",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # # -----------------------------------------
        # # Empty response
        # # -----------------------------------------

        # if not result.content:

        #     error = "MCP server returned no content."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="list_tickets",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # first_content = result.content[0]

        # # -----------------------------------------
        # # Response format validation
        # # -----------------------------------------

        # if not hasattr(first_content, "text"):

        #     error = "Unexpected MCP response format."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="list_tickets",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # # -----------------------------------------
        # # Parse response
        # # -----------------------------------------

        # try:

        #     data = json.loads(
        #         first_content.text
        #     )

        # except json.JSONDecodeError:

        #     error = "Unable to parse MCP tool response."

        #     audit_mcp_execution(
        #         user_id=user_id,
        #         tool_name="list_tickets",
        #         arguments=arguments,
        #         success=False,
        #         error=error,
        #         execution_time_ms=execution_time_ms,
        #     )

        #     return {
        #         "success": False,
        #         "error": error,
        #     }

        # -----------------------------------------
        # Audit MCP result
        # -----------------------------------------

        audit_mcp_execution(
            user_id=user_id,
            tool_name="list_tickets",
            arguments=arguments,
            success=data.get("success", False),
            result=data,
            error=data.get("error"),
            execution_time_ms=execution_time_ms,
        )

        return data

    # ---------------------------------------------
    # Unexpected exception
    # ---------------------------------------------

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        audit_mcp_execution(
            user_id=user_id,
            tool_name="list_tickets",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": str(exc),
        }


async def update_enterprise_ticket(
    ticket_id: int,
    user_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    status: str | None = None,
):
    arguments = {
        "ticket_id": ticket_id,
    }

    if title is not None:
        arguments["title"] = title

    if description is not None:
        arguments["description"] = description

    if priority is not None:
        arguments["priority"] = priority

    if status is not None:
        arguments["status"] = status

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="update_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:
            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="update_ticket",
            )

        except MCPAuthorizationError as exc:
            error = str(exc)

            audit_mcp_denial(
                user_id=user_id,
                tool_name="update_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    start_time = time.perf_counter()

    try:
        result = await update_ticket(
            ticket_id=ticket_id,
            title=title,
            description=description,
            priority=priority,
            status=status,
        )

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        result_data = parse_mcp_response(result)




    #     # Parse MCP response
    #     if hasattr(result, "content"):

    #         content = result.content

    #         if content:
    #             text = getattr(
    #                 content[0],
    #                 "text",
    #                 None
    #             )

    #             if text:
    #                 result_data = json.loads(text)
    #             else:
    #                 result_data = {
    #                     "success": False,
    #                     "error": "Invalid MCP response."
    #                 }

    #         else:
    #             result_data = {
    #                 "success": False,
    #                 "error": "Empty MCP response."
    #             }

    #     elif isinstance(result, dict):
    #         result_data = result

    #     else:
    #         result_data = {
    #             "success": False,
    #             "error": "Unexpected MCP response."
    #         }

        audit_mcp_execution(
            user_id=user_id,
            tool_name="update_ticket",
            arguments=arguments,
            success=result_data.get("success", False),
            result=result_data,
            error=result_data.get("error"),
            execution_time_ms=execution_time_ms,
        )

        return result_data

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )


        audit_mcp_execution(
            user_id=user_id,
            tool_name="update_ticket",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": str(exc),
        }






async def jira_cloud_create_enterprise_ticket(
    project_key: str,
    title: str,
    description: str,
    issue_type: str = "Task",
    user_id: int | None = None,
) -> dict:

    # ---------------------------------------------
    # Validate authenticated user
    # ---------------------------------------------

    if user_id is None:
        return {
            "success": False,
            "error": "Authenticated user is required.",
        }

    arguments = {
        "project_key": project_key,
        "title": title,
        "description": description,
        "issue_type": issue_type,
    }

    # ---------------------------------------------
    # Authentication + Authorization
    # ---------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_create_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="jira_cloud_create_ticket",
            )

        except MCPAuthorizationError as exc:

            error = str(exc)

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_create_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    # ---------------------------------------------
    # Jira Cloud execution
    # ---------------------------------------------

    start_time = time.perf_counter()

    db = SessionLocal()

    try:

        client = JiraClient(
            db=db,
            user_id=user_id,
        )

        result = await client.create_issue(
            project_key=project_key.strip().upper(),
            summary=title.strip(),
            description=description.strip(),
            issue_type=issue_type.strip(),
        )

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        data = {
            "success": True,
            "source": "jira_cloud",
            "message": "Jira issue created successfully.",
            "issue": result,
        }

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_create_ticket",
            arguments=arguments,
            success=True,
            result=data,
            error=None,
            execution_time_ms=execution_time_ms,
        )

        return data

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_create_ticket",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": f"Unable to create Jira Cloud issue: {str(exc)}",
        }

    finally:
        db.close()


async def jira_cloud_get_enterprise_ticket(
    issue_key: str,
    user_id: int,
) -> dict:

    arguments = {
        "issue_key": issue_key,
    }

    # ---------------------------------------------
    # Authentication + Authorization
    # ---------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_get_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="jira_cloud_get_ticket",
            )

        except MCPAuthorizationError as exc:

            error = str(exc)

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_get_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    # ---------------------------------------------
    # Jira Cloud execution
    # ---------------------------------------------

    start_time = time.perf_counter()

    db = SessionLocal()

    try:

        client = JiraClient(
            db=db,
            user_id=user_id,
        )

        result = await client.get_issue(
            issue_key=issue_key.strip().upper()
        )

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        data = {
            "success": True,
            "source": "jira_cloud",
            "issue": result,
        }

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_get_ticket",
            arguments=arguments,
            success=True,
            result=data,
            error=None,
            execution_time_ms=execution_time_ms,
        )

        return data

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_get_ticket",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": f"Unable to retrieve Jira Cloud issue: {str(exc)}",
        }

    finally:
        db.close()


async def jira_cloud_list_enterprise_tickets(
    jql: str,
    max_results: int = 20,
    user_id: int | None = None,
) -> dict:

    if user_id is None:
        return {
            "success": False,
            "error": "Authenticated user is required.",
        }

    arguments = {
        "jql": jql,
        "max_results": max_results,
    }

    # ---------------------------------------------
    # Validate input
    # ---------------------------------------------

    if not jql.strip():
        return {
            "success": False,
            "error": "JQL query cannot be empty.",
        }

    if max_results < 1 or max_results > 100:
        return {
            "success": False,
            "error": "max_results must be between 1 and 100.",
        }

    # ---------------------------------------------
    # Authentication + Authorization
    # ---------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_list_tickets",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="jira_cloud_list_tickets",
            )

        except MCPAuthorizationError as exc:

            error = str(exc)

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_list_tickets",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    # ---------------------------------------------
    # Jira Cloud execution
    # ---------------------------------------------

    start_time = time.perf_counter()

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

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        data = {
            "success": True,
            "source": "jira_cloud",
            "issues": result,
        }

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_list_tickets",
            arguments=arguments,
            success=True,
            result=data,
            error=None,
            execution_time_ms=execution_time_ms,
        )

        return data

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_list_tickets",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": f"Unable to search Jira Cloud issues: {str(exc)}",
        }

    finally:
        db.close()




async def jira_cloud_update_enterprise_ticket(
    issue_key: str,
    user_id: int,
    title: str | None = None,
    description: str | None = None,
) -> dict:

    arguments = {
        "issue_key": issue_key,
    }

    if title is not None:
        arguments["title"] = title

    if description is not None:
        arguments["description"] = description

    # ---------------------------------------------
    # Validate input
    # ---------------------------------------------

    if not issue_key.strip():
        return {
            "success": False,
            "error": "Jira issue key cannot be empty.",
        }

    if title is None and description is None:
        return {
            "success": False,
            "error": "At least one field must be provided for update.",
        }

    # ---------------------------------------------
    # Authentication + Authorization
    # ---------------------------------------------

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            error = "User not found."

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_update_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

        try:

            authorize_mcp_tool(
                db=db,
                user=user,
                tool_name="jira_cloud_update_ticket",
            )

        except MCPAuthorizationError as exc:

            error = str(exc)

            audit_mcp_denial(
                user_id=user_id,
                tool_name="jira_cloud_update_ticket",
                arguments=arguments,
                error=error,
            )

            return {
                "success": False,
                "error": error,
            }

    finally:
        db.close()

    # ---------------------------------------------
    # Jira Cloud execution
    # ---------------------------------------------

    start_time = time.perf_counter()

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

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        data = {
            "success": True,
            "source": "jira_cloud",
            "message": "Jira issue updated successfully.",
            "issue": result,
        }

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_update_ticket",
            arguments=arguments,
            success=True,
            result=data,
            error=None,
            execution_time_ms=execution_time_ms,
        )

        return data

    except Exception as exc:

        execution_time_ms = get_execution_time_ms(
            start_time
        )

        audit_mcp_execution(
            user_id=user_id,
            tool_name="jira_cloud_update_ticket",
            arguments=arguments,
            success=False,
            error=str(exc),
            execution_time_ms=execution_time_ms,
        )

        return {
            "success": False,
            "error": f"Unable to update Jira Cloud issue: {str(exc)}",
        }

    finally:
        db.close()