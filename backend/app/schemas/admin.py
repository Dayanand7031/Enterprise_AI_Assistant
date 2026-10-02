from pydantic import BaseModel, Field




class ApplicationAccessResponse(BaseModel):
    application: str
    enabled: bool


class UpdateApplicationAccessRequest(BaseModel):
    application: str = Field(..., min_length=1)
    enabled: bool


class UserAccessResponse(BaseModel):
    user_id: int
    applications: list[ApplicationAccessResponse]



class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str | None

class AdminUserDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str | None
    applications: list[ApplicationAccessResponse]