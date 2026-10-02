from app.db.database import SessionLocal
from app.services.mcp.mcp_audit_service import create_mcp_audit_log


db = SessionLocal()

try:
    audit = create_mcp_audit_log(
        db=db,
        user_id=5,
        tool_name="update_ticket",
        arguments={
            "ticket_id": 5,
            "priority": "high"
        },
        success=False,
        error="Permission required: jira:update",
    )

    print("Audit created successfully.")

    print("ID:", audit.id)
    print("User ID:", audit.user_id)
    print("Tool:", audit.tool_name)
    print("Arguments:", audit.arguments)
    print("Success:", audit.success)
    print("Error:", audit.error)

finally:
    db.close()