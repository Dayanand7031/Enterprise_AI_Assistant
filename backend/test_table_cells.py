from pathlib import Path
import pymupdf


pdf_file = next(Path("uploads").glob("*.pdf"))

document = pymupdf.open(pdf_file)

try:
    page = document[1]

    finder = page.find_tables()
    table = finder.tables[0]

    print("=" * 70)
    print("PAGE 2 CELL GEOMETRY")
    print("=" * 70)

    for row_index, row in enumerate(
        table.rows,
        start=1
    ):

        print(f"\nROW {row_index}")
        print("-" * 70)

        print(f"Row bbox: {row.bbox}")

        for cell_index, cell in enumerate(
            row.cells,
            start=1
        ):

            print(
                f"Cell {cell_index}: "
                f"bbox={cell} "
            )

finally:
    document.close()