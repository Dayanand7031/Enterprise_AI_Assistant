import pymupdf
from docx import Document


def extract_pdf_text(file_path: str) -> list[dict]:
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        pages.append({
            "page": page_number,
            "text": text
        })

    document.close()

    return pages


def extract_docx_text(file_path: str) -> list[dict]:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return [
        {
            "page": 1,
            "text": "\n".join(paragraphs)
        }
    ]


def extract_document_text(
    file_path: str,
    file_extension: str
) -> list[dict]:

    extension = file_extension.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )


def extract_pdf_text_without_tables(
    file_path: str,
    table_bboxes_by_page: dict[int, list[tuple]]
) -> list[dict]:
    """
    Extract PDF text while removing text blocks
    that belong to detected table regions.
    """

    document = pymupdf.open(file_path)

    pages = []

    try:
        for page_number, page in enumerate(
            document,
            start=1
        ):

            table_bboxes = table_bboxes_by_page.get(
                page_number,
                []
            )

            blocks = page.get_text("blocks")

            filtered_blocks = []

            for block in blocks:

                x0, y0, x1, y1 = block[:4]
                text = block[4]

                if not text.strip():
                    continue

                block_rect = pymupdf.Rect(
                    x0,
                    y0,
                    x1,
                    y1
                )

                belongs_to_table = False

                for bbox in table_bboxes:

                    table_rect = pymupdf.Rect(bbox)

                    # Expand the table region slightly.
                    # This handles PDF text blocks that
                    # extend slightly outside the detected
                    # table bounding box.
                    table_rect.x0 -= 5
                    table_rect.y0 -= 10
                    table_rect.x1 += 5
                    table_rect.y1 += 25

                    # -------------------------------------
                    # Check 1: overlap percentage
                    # -------------------------------------

                    intersection = (
                        block_rect & table_rect
                    )

                    if not intersection.is_empty:

                        block_area = (
                            block_rect.get_area()
                        )

                        if block_area > 0:

                            overlap_ratio = (
                                intersection.get_area()
                                / block_area
                            )

                            if overlap_ratio >= 0.5:
                                belongs_to_table = True
                                break

                    # -------------------------------------
                    # Check 2: block center
                    # -------------------------------------

                    block_center = block_rect.tl + (
                        block_rect.br
                        - block_rect.tl
                    ) * 0.5

                    if table_rect.contains(
                        block_center
                    ):
                        belongs_to_table = True
                        break

                # -----------------------------------------
                # Keep only non-table text blocks
                # -----------------------------------------

                if not belongs_to_table:

                    filtered_blocks.append(
                        (x0, y0, x1, y1, text)
                    )

            # ---------------------------------------------
            # Preserve approximate reading order
            # ---------------------------------------------

            filtered_blocks.sort(
                key=lambda block: (
                    block[1],
                    block[0]
                )
            )

            page_text = "\n".join(
                block[4].strip()
                for block in filtered_blocks
                if block[4].strip()
            )

            pages.append({
                "page": page_number,
                "text": page_text
            })

    finally:
        document.close()

    return pages