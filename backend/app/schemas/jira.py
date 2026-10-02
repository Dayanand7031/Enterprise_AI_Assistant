from datetime import datetime

from pydantic import BaseModel, Field
from typing import Literal


class JiraTicketCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    description: str = Field(
        ...,
        min_length=1
    )

    priority: Literal[
        "low",
        "medium",
        "high",
        "critical"
    ] = "medium"


class JiraTicketUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        min_length=1
    )

    priority: str | None = None

    status: str | None = None


class JiraTicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    created_by: int | None
    created_at: datetime | None

    model_config = {
        "from_attributes": True
    }