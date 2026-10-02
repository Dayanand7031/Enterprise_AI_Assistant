from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    file_type: str
    file_size: int
    message: str
    text_preview: str