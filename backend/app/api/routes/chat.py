from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.auth.dependencies import get_current_user
from app.models.auth_model import User, Conversation, Message
from app.db.database import get_db

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation.conversation_service import (
    get_conversation_history,
)
from app.graph.workflow import chat_graph


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # --------------------------------------------------
    # 1. Get existing conversation OR create new one
    # --------------------------------------------------

    if request.conversation_id is not None:

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id,
            )
            .first()
        )

        # IMPORTANT:
        # Do not silently create a new conversation
        # if the requested conversation doesn't belong
        # to this user.
        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

    else:

        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50],
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # --------------------------------------------------
    # 2. Load previous conversation history
    # --------------------------------------------------

    history = get_conversation_history(
        db=db,
        conversation_id=conversation.id,
        limit=6,
    )

    # --------------------------------------------------
    # 3. Save current user message
    # --------------------------------------------------

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    db.add(user_message)

    # Update conversation activity timestamp
    conversation.updated_at = datetime.now(timezone.utc)

    db.commit()

    # --------------------------------------------------
    # 4. Run LangGraph
    # --------------------------------------------------

    result = await chat_graph.ainvoke(
        {
            "query": request.message,
            "history": history,
            "user_id": current_user.id,
        }
    )

    answer = result["answer"]
    sources = result["sources"]

    # --------------------------------------------------
    # 5. Save assistant response
    # --------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
    )

    db.add(assistant_message)

    # Update conversation activity again
    conversation.updated_at = datetime.now(timezone.utc)

    db.commit()

    # --------------------------------------------------
    # 6. Return response
    # --------------------------------------------------

    return ChatResponse(
        conversation_id=conversation.id,
        answer=answer,
        sources=sources,
    )