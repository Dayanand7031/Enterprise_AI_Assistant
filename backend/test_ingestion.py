from pathlib import Path

from app.services.rag.ingestion_service import (
    ingest_pdf
)


UPLOAD_DIR = Path("uploads")


print("=" * 70)
print("UNIFIED INGESTION TEST")
print("=" * 70)


pdf_files = list(
    UPLOAD_DIR.glob("*.pdf")
)

if not pdf_files:
    print("ERROR: No PDF files found.")
    raise SystemExit(1)


file_path = pdf_files[0]

print(
    f"\nPDF: {file_path.name}"
)


documents = ingest_pdf(
    str(file_path),
    filename=file_path.name
)


print(
    f"\nTOTAL RAG DOCUMENTS: "
    f"{len(documents)}"
)


# =============================================================
# SUMMARY
# =============================================================

text_documents = [
    document
    for document in documents
    if document["metadata"]["content_type"] == "text"
]

table_documents = [
    document
    for document in documents
    if document["metadata"]["content_type"] == "table"
]


print(
    f"\nText documents: "
    f"{len(text_documents)}"
)

print(
    f"Table documents: "
    f"{len(table_documents)}"
)


# =============================================================
# TABLE TYPES
# =============================================================

table_types = {}

for document in table_documents:

    table_type = document[
        "metadata"
    ].get(
        "table_type",
        "unknown"
    )

    table_types[table_type] = (
        table_types.get(
            table_type,
            0
        ) + 1
    )


print("\nTable document breakdown:")

for table_type, count in table_types.items():

    print(
        f"  {table_type}: {count}"
    )


# =============================================================
# DISPLAY DOCUMENTS
# =============================================================

for index, document in enumerate(
    documents,
    start=1
):

    print("\n" + "=" * 70)

    print(
        f"DOCUMENT {index}"
    )

    print("=" * 70)

    print("\nCONTENT:")

    print(
        document["text"]
    )

    print("\nMETADATA:")

    for key, value in (
        document["metadata"].items()
    ):

        print(
            f"{key}: {value}"
        )


print("\n" + "=" * 70)
print("UNIFIED INGESTION TEST COMPLETED")
print("=" * 70)