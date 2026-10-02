from pydantic import BaseModel, Field

class JiraIssueSearchRequest(BaseModel):

    jql: str = Field(..., min_length=1)
    max_results: int = Field(default=20, ge=1, le=100)