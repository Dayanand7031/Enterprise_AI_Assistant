from app.db.database import SessionLocal
from app.services.jira.jira_service import (
    create_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
)
from app.schemas.jira import (
    JiraTicketCreate,
    JiraTicketUpdate,
)


db = SessionLocal()


try:
    # --------------------------------------------------
    # 1. CREATE
    # --------------------------------------------------

    create_data = JiraTicketCreate(
        title="Login page not working",
        description="Users receive a 500 error when attempting to log in.",
        priority="high",
    )

    ticket = create_ticket(
        db=db,
        ticket_data=create_data,
        created_by=current_user.id,
    )

    print("\n========== CREATED TICKET ==========")
    print("ID:", ticket.id)
    print("Title:", ticket.title)
    print("Priority:", ticket.priority)
    print("Status:", ticket.status)
    print("Created By:", ticket.created_by)
    print("Created At:", ticket.created_at)


    # --------------------------------------------------
    # 2. GET
    # --------------------------------------------------

    fetched_ticket = get_ticket(
        db=db,
        ticket_id=ticket.id,
    )

    print("\n========== GET TICKET ==========")

    if fetched_ticket:
        print("ID:", fetched_ticket.id)
        print("Title:", fetched_ticket.title)
        print("Description:", fetched_ticket.description)
        print("Priority:", fetched_ticket.priority)
        print("Status:", fetched_ticket.status)
    else:
        print("Ticket not found.")


    # --------------------------------------------------
    # 3. LIST
    # --------------------------------------------------

    tickets = list_tickets(db=db)

    print("\n========== ALL TICKETS ==========")

    for item in tickets:
        print(
            f"ID={item.id} | "
            f"Title={item.title} | "
            f"Priority={item.priority} | "
            f"Status={item.status}"
        )


    # --------------------------------------------------
    # 4. UPDATE
    # --------------------------------------------------

    update_data = JiraTicketUpdate(
        status="in_progress",
        priority="critical",
    )

    updated_ticket = update_ticket(
        db=db,
        ticket_id=ticket.id,
        ticket_data=update_data,
    )

    print("\n========== UPDATED TICKET ==========")

    if updated_ticket:
        print("ID:", updated_ticket.id)
        print("Title:", updated_ticket.title)
        print("Priority:", updated_ticket.priority)
        print("Status:", updated_ticket.status)
    else:
        print("Ticket not found.")


finally:
    db.close()