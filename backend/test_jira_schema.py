from app.schemas.jira import (
    JiraTicketCreate,
    JiraTicketUpdate,
)


ticket = JiraTicketCreate(
    title="Login page not working",
    description="Users receive a 500 error.",
    priority="high",
)

print("CREATE SCHEMA:")
print(ticket.model_dump())


update = JiraTicketUpdate(
    status="in_progress",
)

print("\nUPDATE SCHEMA:")
print(update.model_dump())