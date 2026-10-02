from app.services.rag.ingestion_service import ingest_pdf
from app.services.rag.vector_store_service import (
    add_documents,
    get_collection_count,
)


PDF_PATH = "uploads/c3b21bf361394dee80c316d968ddbb57.pdf"
FILENAME = "Revised Employee Leave Policy 2026-2027.pdf"


print("=" * 70)
print("CHROMADB VECTOR STORE TEST")
print("=" * 70)


# ---------------------------------------------
# 1. Run document ingestion
# ---------------------------------------------

documents = ingest_pdf(
    PDF_PATH,
    FILENAME
)

print("\nIngestion completed.")
print("RAG documents:", len(documents))


# ---------------------------------------------
# 2. Store documents in ChromaDB
# ---------------------------------------------

add_documents(documents)

print("Documents added to ChromaDB.")


# ---------------------------------------------
# 3. Check collection
# ---------------------------------------------

count = get_collection_count()

print("\nChromaDB document count:", count)


print("\nVector store test completed.")