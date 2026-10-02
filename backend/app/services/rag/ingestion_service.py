from app.services.rag.document_service import (
    extract_document_text
)

from app.services.rag.chunking_service import (
    chunk_pages
)

from app.services.rag.table_extraction_service import (
    extract_tables_from_pdf
)

from app.services.rag.table_normalization_service import (
    create_leave_chunks,
    create_holiday_chunks,
    create_generic_table_chunks,
    
)
from app.services.rag.document_service import extract_pdf_text_without_tables


def ingest_pdf(file_path: str, filename: str) -> list[dict]:

    documents = []

    # --------------------------------------------------
    # 1. Detect tables first
    # --------------------------------------------------

    tables = extract_tables_from_pdf(file_path)

    # Group table bounding boxes by page.
    table_bboxes_by_page: dict[int, list[tuple]] = {}

    for table in tables:

        page_number = table["page"]
        bbox = table["bbox"]

        table_bboxes_by_page.setdefault(
            page_number,
            []
        ).append(bbox)

    # --------------------------------------------------
    # 2. Extract normal text WITHOUT table content
    # --------------------------------------------------

    pages = extract_pdf_text_without_tables(
        file_path,
        table_bboxes_by_page
    )

    text_chunks = chunk_pages(
        pages,
        filename=filename
    )

    for chunk in text_chunks:

        chunk["metadata"]["content_type"] = "text"

        documents.append(chunk)

    # --------------------------------------------------
    # 3. Convert tables into structured RAG documents
    # --------------------------------------------------

    for table in tables:

        page = table["page"]

        if page == 2:

            chunks = create_leave_chunks(
                table,
                filename
            )

        elif page == 4:

            chunks = create_holiday_chunks(
                table,
                filename
            )

        else:

            chunks = create_generic_table_chunks(
                table,
                filename
            )

        documents.extend(chunks)

    return documents