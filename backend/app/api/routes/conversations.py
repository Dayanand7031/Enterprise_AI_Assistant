from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationDetail,
    ConversationSummary,
)
from app.services.auth.dependencies import get_current_user
from app.services.conversation.conversation_service import (
    create_conversation_service,
    delete_conversation_service,
    get_conversation_service,
    list_conversations_service,
)

router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.get(
    "/",
    response_model=list[ConversationSummary],
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_conversations_service(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_conversation_service(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )


@router.post(
    "/",
    response_model=ConversationSummary,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_conversation_service(
        db=db,
        user_id=current_user.id,
        title=data.title,
    )


@router.delete(
    "/{conversation_id}",
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return delete_conversation_service(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )