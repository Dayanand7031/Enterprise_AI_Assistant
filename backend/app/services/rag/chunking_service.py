from langchain_text_splitters import RecursiveCharacterTextSplitter


def clean_page_text(text: str) -> str:

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove repeated company header information
        if line.startswith("TSF Engineers Pvt. Ltd."):
            continue

        if line.startswith("Corporate Office:"):
            continue

        if line.startswith("Registered Office:"):
            continue

        if line.startswith("Phone:"):
            continue

        if line.startswith("Phone"):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def chunk_pages(
    pages: list[dict],
    filename: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 300
) -> list[dict]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    chunk_index = 0

    for page in pages:

        text = clean_page_text(
            page["text"]
        )

        if not text.strip():
            continue

        page_chunks = splitter.split_text(text)

        for chunk in page_chunks:

            chunks.append({
                "text": chunk,
                "metadata": {
                    "filename": filename,
                    "page": page["page"],
                    "chunk_index": chunk_index
                }
            })

            chunk_index += 1

    return chunks