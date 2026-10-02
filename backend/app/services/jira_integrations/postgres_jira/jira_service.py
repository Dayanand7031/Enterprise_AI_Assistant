from sqlalchemy.orm import Session

from app.models.jira_ticket_model import JiraTicket
from app.schemas.jira import (
    JiraTicketCreate,
    JiraTicketUpdate,
)


def create_ticket(
    db: Session,
    ticket_data: JiraTicketCreate,
    created_by: int | None = None,
) -> JiraTicket:

    ticket = JiraTicket(
        title=ticket_data.title.strip(),
        description=ticket_data.description.strip(),
        priority=ticket_data.priority,
        status="open",
        created_by=created_by,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_ticket(
    db: Session,
    ticket_id: int,
) -> JiraTicket | None:

    return (
        db.query(JiraTicket)
        .filter(JiraTicket.id == ticket_id)
        .first()
    )


def list_tickets(
    db: Session,
) -> list[JiraTicket]:

    return (
        db.query(JiraTicket)
        .order_by(JiraTicket.created_at.desc())
        .all()
    )


def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_data: JiraTicketUpdate,
) -> JiraTicket | None:

    ticket = get_ticket(
        db=db,
        ticket_id=ticket_id,
    )

    if ticket is None:
        return None

    update_data = ticket_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()

        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)

    return ticket