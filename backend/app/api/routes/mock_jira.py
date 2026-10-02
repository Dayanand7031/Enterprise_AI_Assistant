from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.auth_model import User
from app.db.database import get_db
from app.schemas.jira import (
    JiraTicketCreate,
    JiraTicketResponse,
    JiraTicketUpdate,
)

from app.services.rbac.dependencies import require_permission
from app.services.jira_integrations.postgres_jira.jira_service import (
    create_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
)
from app.services.auth.dependencies  import get_current_user


router = APIRouter(
    prefix="/api/jira",
    tags=["Mock Jira"],
)


@router.post(
    "/tickets",
    response_model=JiraTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_jira_ticket(
    ticket_data: JiraTicketCreate,
    db: Session = Depends(get_db),
    current_user: User= Depends(require_permission("jira:create"))
):
    ticket = create_ticket(
        db=db,
        ticket_data=ticket_data,
        created_by=current_user.id,
    )

    return ticket


@router.get(
    "/tickets",
    response_model=list[JiraTicketResponse],
)
def get_jira_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("jira:read")),
):
    tickets = list_tickets(db=db)

    return tickets


@router.get(
    "/tickets/{ticket_id}",
    response_model=JiraTicketResponse,
)
def get_jira_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("jira:update")),
):
    ticket = get_ticket(
        db=db,
        ticket_id=ticket_id,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jira ticket {ticket_id} not found.",
        )

    return ticket


@router.put(
    "/tickets/{ticket_id}",
    response_model=JiraTicketResponse,
)
def update_jira_ticket(
    ticket_id: int,
    ticket_data: JiraTicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = update_ticket(
        db=db,
        ticket_id=ticket_id,
        ticket_data=ticket_data,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jira ticket {ticket_id} not found.",
        )

    return ticket