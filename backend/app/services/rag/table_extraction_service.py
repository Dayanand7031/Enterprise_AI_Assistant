import pymupdf


def extract_tables_from_pdf(
    file_path: str
) -> list[dict]:
    """
    Extract all detected tables from a PDF.

    Returns normalized raw table structures containing:
    - page
    - table index
    - headers
    - rows
    """

    document = pymupdf.open(file_path)

    tables = []

    try:

        for page_number, page in enumerate(
            document,
            start=1
        ):

            try:
                table_finder = page.find_tables()

            except Exception:
                continue

            for table_index, table in enumerate(
                table_finder.tables,
                start=1
            ):

                extracted = table.extract()

                if not extracted:
                    continue

                headers = extracted[0]
                rows = extracted[1:]

                tables.append({
                "page": page_number,
                "table_index": table_index,
                "bbox": table.bbox,
                "headers": headers,
                "rows": rows,
            })

    finally:
        document.close()

    return tables