from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import DocumentUploadResponse
from app.services.rag.document_service import extract_document_text

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


UPLOAD_DIR = Path("uploads")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
}


@router.post(
    "/upload",
    response_model=DocumentUploadResponse
)
async def upload_document(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    unique_filename = (
        f"{uuid4().hex}{file_extension}"
    )

    file_path = UPLOAD_DIR / unique_filename

    file_content = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    try:
        extracted_pages = extract_document_text(
            str(file_path),
            file_extension
        )
       
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract document text: {str(exc)}"
        )
    
    text_preview = "\n".join(
        page["text"]
        for page in extracted_pages
    )

    return DocumentUploadResponse(
        filename=file.filename,
        file_type=file_extension.replace(".", "").upper(),
        file_size=len(file_content),
        message="Document uploaded successfully.",
        text_preview=text_preview[:1000]
    )