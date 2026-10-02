from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class ChatSource(BaseModel):
    filename: str | None = None
    page: int | None = None
    content_type: str | None = None
    table_type: str | None = None
    distance: float | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    sources: list[ChatSource] = []