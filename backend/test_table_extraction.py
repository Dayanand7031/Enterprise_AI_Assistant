from pathlib import Path

import pymupdf


UPLOAD_DIR = Path("uploads")


print("=" * 70)
print("TABLE GEOMETRY TEST")
print("=" * 70)


pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("ERROR: No PDF files found.")
    raise SystemExit(1)


file_path = pdf_files[0]

print(f"\nPDF: {file_path.name}")


document = pymupdf.open(file_path)


try:

    for page_number, page in enumerate(
        document,
        start=1
    ):

        print("\n" + "=" * 70)
        print(f"PAGE {page_number}")
        print("=" * 70)

        try:
            table_finder = page.find_tables()
        except Exception as exc:
            print(
                f"Table detection failed: {exc}"
            )
            continue

        print(
            f"Tables detected: "
            f"{len(table_finder.tables)}"
        )

        for table_index, table in enumerate(
            table_finder.tables,
            start=1
        ):

            print("\n" + "-" * 70)
            print(f"TABLE {table_index}")
            print("-" * 70)

            print(
                f"Bounding box: {table.bbox}"
            )

            print(
                f"Rows detected: "
                f"{len(table.rows)}"
            )

            # --------------------------------------------------
            # EXTRACT TABLE
            # --------------------------------------------------

            extracted = table.extract()

            if not extracted:
                print("No extracted data.")
                continue

            print(
                f"Columns detected: "
                f"{len(extracted[0])}"
            )

            # --------------------------------------------------
            # PRINT ROW/COLUMN STRUCTURE
            # --------------------------------------------------

            for row_index, row in enumerate(
                extracted,
                start=1
            ):

                print(
                    f"\nRow {row_index}"
                )

                for column_index, cell in enumerate(
                    row,
                    start=1
                ):

                    print(
                        f"  Column {column_index}: "
                        f"{repr(cell)}"
                    )

finally:
    document.close()


print("\n" + "=" * 70)
print("GEOMETRY TEST COMPLETED")
print("=" * 70)