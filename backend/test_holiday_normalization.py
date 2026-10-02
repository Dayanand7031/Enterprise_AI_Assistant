from pathlib import Path

from app.services.rag.document_service import (
    extract_document_text
)

from app.services.rag.table_extraction_service import (
    extract_tables_from_pdf
)

from app.services.rag.table_normalization_service import (
    create_holiday_chunks
)


UPLOAD_DIR = Path("uploads")


print("=" * 70)
print("HOLIDAY TABLE NORMALIZATION TEST")
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


# -------------------------------------------------------------
# Extract tables
# -------------------------------------------------------------

tables = extract_tables_from_pdf(
    str(file_path)
)


# -------------------------------------------------------------
# Find page 4 holiday table
# -------------------------------------------------------------

holiday_table = None

for table in tables:

    if table["page"] == 4:

        holiday_table = table
        break


if holiday_table is None:

    print(
        "\nERROR: Holiday table not found."
    )

    raise SystemExit(1)


# -------------------------------------------------------------
# Normalize
# -------------------------------------------------------------

chunks = create_holiday_chunks(
    holiday_table,
    filename=file_path.name
)


print(
    f"\nNormalized holidays: "
    f"{len(chunks)}"
)


# -------------------------------------------------------------
# Display
# -------------------------------------------------------------

for index, chunk in enumerate(
    chunks,
    start=1
):

    print("\n" + "=" * 70)

    print(
        f"HOLIDAY {index}"
    )

    print("=" * 70)

    print("\nTEXT:")

    print(
        chunk["text"]
    )

    print("\nMETADATA:")

    for key, value in (
        chunk["metadata"].items()
    ):

        print(
            f"{key}: {value}"
        )


print("\n" + "=" * 70)
print("HOLIDAY NORMALIZATION TEST COMPLETED")
print("=" * 70)