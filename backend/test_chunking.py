from pathlib import Path

from app.services.rag.document_service import extract_document_text
from app.services.rag.chunking_service import chunk_pages


# --------------------------------------------------
# Configuration
# --------------------------------------------------

UPLOAD_DIR = Path("uploads")


# --------------------------------------------------
# Check uploads directory
# --------------------------------------------------

print("=" * 70)
print("CHUNKING TEST")
print("=" * 70)

print(f"Upload directory: {UPLOAD_DIR.resolve()}")

if not UPLOAD_DIR.exists():
    print("\nERROR: uploads directory does not exist.")
    raise SystemExit(1)


# --------------------------------------------------
# Find uploaded files
# --------------------------------------------------

files = list(UPLOAD_DIR.iterdir())

print(f"\nFiles found: {len(files)}")

for file in files:
    print(f" - {file.name}")


# --------------------------------------------------
# Find PDF / DOCX
# --------------------------------------------------

supported_files = [
    file
    for file in files
    if file.suffix.lower() in {".pdf", ".docx"}
]


if not supported_files:
    print("\nERROR: No PDF or DOCX files found.")
    raise SystemExit(1)


# --------------------------------------------------
# Select first document
# --------------------------------------------------

file_path = supported_files[0]

print("\n" + "=" * 70)
print("SELECTED DOCUMENT")
print("=" * 70)

print(f"Filename: {file_path.name}")
print(f"Extension: {file_path.suffix}")


# --------------------------------------------------
# Extract document
# --------------------------------------------------

print("\n" + "=" * 70)
print("EXTRACTING DOCUMENT")
print("=" * 70)

try:
    pages = extract_document_text(
        str(file_path),
        file_path.suffix.lower()
    )

except Exception as exc:
    print("\nERROR DURING EXTRACTION:")
    print(type(exc).__name__)
    print(str(exc))
    raise


print(f"\nTotal pages: {len(pages)}")


# --------------------------------------------------
# Display extracted pages
# --------------------------------------------------

for page in pages:

    print("\n" + "-" * 70)
    print(f"PAGE {page['page']}")
    print("-" * 70)

    text = page["text"]

    print(f"Characters: {len(text)}")

    print("\nPreview:")
    print(text[:500])


# --------------------------------------------------
# Chunk document
# --------------------------------------------------

print("\n" + "=" * 70)
print("CREATING CHUNKS")
print("=" * 70)

try:

    chunks = chunk_pages(
        pages,
        filename=file_path.name
    )

except Exception as exc:

    print("\nERROR DURING CHUNKING:")
    print(type(exc).__name__)
    print(str(exc))

    raise


# --------------------------------------------------
# Display chunks
# --------------------------------------------------

print(f"\nTOTAL CHUNKS: {len(chunks)}")


for chunk in chunks:

    print("\n" + "=" * 70)

    print(
        f"CHUNK {chunk['metadata']['chunk_index']}"
    )

    print("=" * 70)

    print("\nTEXT:")

    print(chunk["text"])

    print("\nMETADATA:")

    print(chunk["metadata"])


# --------------------------------------------------
# Complete
# --------------------------------------------------

print("\n" + "=" * 70)
print("CHUNKING TEST COMPLETED")
print("=" * 70)