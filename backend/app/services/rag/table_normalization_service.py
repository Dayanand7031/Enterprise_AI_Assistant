from typing import Any


def clean_cell(value: Any) -> str:
    """
    Normalize a single table cell.
    """

    if value is None:
        return ""

    return " ".join(
        str(value)
        .replace("\n", " ")
        .split()
    )


def get_cell(
    row: list,
    index: int
) -> str:
    """
    Safely retrieve and clean a cell.
    """

    if index >= len(row):
        return ""

    return clean_cell(row[index])


def first_non_empty(
    row: list,
    indexes: list[int]
) -> str:
    """
    Return the first non-empty value from
    the supplied indexes.
    """

    for index in indexes:

        value = get_cell(
            row,
            index
        )

        if value:
            return value

    return ""


def normalize_generic_table(
    table: dict
) -> list[dict]:
    """
    Normalize a generic table into key/value
    records where possible.
    """

    headers = [
        clean_cell(value)
        for value in table["headers"]
    ]

    rows = [
        [
            clean_cell(cell)
            for cell in row
        ]
        for row in table["rows"]
    ]

    records = []

    for row in rows:

        record = {}

        for index, value in enumerate(row):

            if not value:
                continue

            if index < len(headers):
                header = headers[index]

                if header:
                    record[header] = value

        if record:
            records.append(record)

    return records

def generic_record_to_text(
    record: dict
) -> str:
    """
    Convert a generic table record into
    semantic text.
    """

    lines = []

    for key, value in record.items():

        lines.append(
            f"{key}: {value}"
        )

    return "\n".join(lines)


def create_generic_table_chunks(
    table: dict,
    filename: str
) -> list[dict]:
    """
    Create RAG-ready chunks from a generic table.
    """

    records = normalize_generic_table(
        table
    )

    chunks = []

    for index, record in enumerate(
        records
    ):

        chunks.append({
            "text": generic_record_to_text(
                record
            ),

            "metadata": {
                "filename": filename,
                "page": table["page"],
                "table_index": table["table_index"],
                "content_type": "table",
                "table_type": "generic",
                "chunk_index": index,
            }
        })

    return chunks

def normalize_leave_table(
    table: dict
) -> list[dict]:
    """
    Convert the leave entitlement table into
    semantic records.

    PyMuPDF returns:

        rows[0] -> header continuation
        rows[1] -> Applicability
        rows[2] -> Entitlement
        rows[3] -> Encashment
    """

    rows = table["rows"]

    if len(rows) < 4:
        return []

    applicability = rows[1]
    entitlement = rows[2]
    encashment = rows[3]

    leave_columns = {
    "Privilege Leave": [1],

    "Sick Leave": [4],

    "Casual Leave": [5],

    "Maternity Leave": [8],

    "Marital Leave": [11],

    "Paternity Leave": [14],

    "Comp Off": [16],
}

    records = []

    for leave_type, columns in leave_columns.items():

        record = {
            "leave_type": leave_type,

            "applicability": first_non_empty(
                applicability,
                columns
            ),

            "entitlement": first_non_empty(
                entitlement,
                columns
            ),

            "encashment": first_non_empty(
                encashment,
                columns
            ),
        }

        if any(
            record[field]
            for field in [
                "applicability",
                "entitlement",
                "encashment",
            ]
        ):
            records.append(record)

    return records


def leave_record_to_text(
    record: dict
) -> str:
    """
    Convert a leave record into a self-contained
    semantic document for RAG.
    """

    lines = [
        f"Leave Type: {record['leave_type']}"
    ]

    if record["applicability"]:
        lines.append(
            f"Applicability: "
            f"{record['applicability']}"
        )

    if record["entitlement"]:
        lines.append(
            f"Entitlement: "
            f"{record['entitlement']}"
        )

    if record["encashment"]:
        lines.append(
            f"Encashment: "
            f"{record['encashment']}"
        )

    return "\n".join(lines)


def create_leave_chunks(
    table: dict,
    filename: str
) -> list[dict]:
    """
    Create RAG-ready chunks from the leave table.
    """

    records = normalize_leave_table(
        table
    )

    chunks = []

    for index, record in enumerate(
        records
    ):

        chunks.append({
            "text": leave_record_to_text(
                record
            ),

            "metadata": {
                "filename": filename,
                "page": table["page"],
                "table_index": table["table_index"],
                "content_type": "table",
                "table_type": "leave_entitlement",
                "leave_type": record["leave_type"],
                "chunk_index": index,
            }
        })

    return chunks


def normalize_holiday_table(
    table: dict
) -> list[dict]:
    """
    Convert the holiday calendar table into
    one semantic record per holiday.

    The PDF uses multiple physical columns because
    of merged cells, but logically each record contains:

        date
        day
        holiday
    """

    rows = table["rows"]

    # The first row is the table header continuation.
    # Actual holiday records start after the
    # Date / Day / Holiday row.

    if len(rows) < 2:
        return []

    holiday_records = []

    for row in rows[1:]:

        if not row:
            continue

        # -----------------------------------------------------
        # Based on the actual PDF structure:
        #
        # Date    → column 1
        # Day     → column 3
        # Holiday → column 6 or 7
        #
        # Some holiday names appear in column 7 instead of 6
        # because of merged cells.
        # -----------------------------------------------------

        date = first_non_empty(
            row,
            [1, 0]
        )

        day = get_cell(
            row,
            3
        )

        holiday = first_non_empty(
            row,
            [6, 7]
        )

        # Ignore rows that contain no holiday information.
        if not (
            date
            or day
            or holiday
        ):
            continue

        holiday_records.append({
            "date": date,
            "day": day,
            "holiday": holiday,
        })

    return holiday_records



def holiday_record_to_text(
    record: dict
) -> str:
    """
    Convert one holiday record into a
    self-contained RAG document.
    """

    lines = [
        f"Holiday: {record['holiday']}"
    ]

    if record["date"]:
        lines.append(
            f"Date: {record['date']}"
        )

    if record["day"]:
        lines.append(
            f"Day: {record['day']}"
        )

    return "\n".join(lines)



def create_holiday_chunks(
    table: dict,
    filename: str
) -> list[dict]:
    """
    Create RAG-ready chunks from the
    holiday calendar table.
    """

    records = normalize_holiday_table(
        table
    )

    chunks = []

    for index, record in enumerate(
        records
    ):

        chunks.append({
            "text": holiday_record_to_text(
                record
            ),

            "metadata": {
                "filename": filename,
                "page": table["page"],
                "table_index": table["table_index"],
                "content_type": "table",
                "table_type": "holiday_calendar",
                "holiday": record["holiday"],
                "date": record["date"],
                "chunk_index": index,
            }
        })

    return chunks

