from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repository.conversation_repository import (
    create_conversation,
    delete_conversation,
    get_user_conversation,
    get_user_conversations,
)
from app.models.auth_model import Message


def get_conversation_history(
    db: Session,
    conversation_id: int,
    limit: int = 6,
) -> list[dict]:

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(
            Message.created_at.desc(),
            Message.id.desc(),
        )
        .limit(limit)
        .all()
    )

    # Newest → oldest from DB.
    # Reverse so the LLM receives chronological history.
    messages.reverse()

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


def list_conversations_service(
    db: Session,
    user_id: int,
):
    return get_user_conversations(
        db=db,
        user_id=user_id,
    )


def get_conversation_service(
    db: Session,
    conversation_id: int,
    user_id: int,
):
    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return conversation


def create_conversation_service(
    db: Session,
    user_id: int,
    title: str = "New Conversation",
):
    title = title.strip()

    if not title:
        title = "New Conversation"

    if len(title) > 255:
        title = title[:255]

    return create_conversation(
        db=db,
        user_id=user_id,
        title=title,
    )


def delete_conversation_service(
    db: Session,
    conversation_id: int,
    user_id: int,
):
    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    delete_conversation(
        db=db,
        conversation=conversation,
    )

    return {
        "message": "Conversation deleted successfully.",
        "conversation_id": conversation_id,
    }