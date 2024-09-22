import argparse
import csv
import logging
from pathlib import Path
from typing import Any, Iterable, List, Sequence, Tuple

from googleapiclient.discovery import build, Resource
from google.oauth2.service_account import Credentials


# The ID and range of the target spreadsheet.
SPREADSHEET_ID = "1ZNIRMp2ra8yo6GJSX2wDFSjsdDMQu7o-173ue-zQsm0"
SHEET_NAME = "Imported"
# Columns (0-index) to use identify rows and detect duplicates
COLUMNS_FOR_DEDUPLICATION = (0, 1)


def connect(credentials_path: Path) -> Resource:
    credentials = Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=credentials)


def load_csv(path: Path) -> Iterable[List[Any]]:
    with open(path, newline="") as file:
        yield from csv.reader(file)


def fetch_rows(resource: Resource) -> List[List[Any]]:
    existing_values = resource.spreadsheets().values()
    request = existing_values.get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME,
        valueRenderOption="UNFORMATTED_VALUE",
    )
    result = request.execute()
    return result.get("values", [])


def deduplicate(
    new_rows: Iterable[List[Any]],
    existing_rows: Iterable[List[Any]],
    columns_to_use: Sequence[int] = COLUMNS_FOR_DEDUPLICATION,
) -> Iterable[List[Any]]:
    logger = logging.getLogger(__name__)

    def row_to_key(row: List[Any]) -> Tuple[Any, ...]:
        return tuple(row[col] for col in columns_to_use)

    row_set = set(row_to_key(row) for row in existing_rows)
    for new_row in new_rows:
        key = row_to_key(new_row)
        if key in row_set:
            # We've seen this row before. Skip it.
            logger.debug("Skipping duplicate row: %s", key)
            continue
        row_set.add(key)
        yield new_row


def append_rows(
    resource: Resource,
    rows: List[List[Any]],
) -> int:
    body = {"values": rows}
    existing_values = resource.spreadsheets().values()
    request = existing_values.append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="RAW",
        includeValuesInResponse=False,
        body=body,
    )
    result = request.execute()
    return result.get("updates", {}).get("updatedRows", 0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="",
    )
    parser.add_argument(
        "credentials_file",
        type=Path,
        help="JSON file containing Google credentials",
    )
    parser.add_argument(
        "file_to_export",
        type=Path,
        help="CSV file to export to Google Sheets",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    resource = connect(args.credentials_file)
    existing_rows = fetch_rows(resource)
    logger.info("Fetched %d rows", len(existing_rows))
    input_rows = load_csv(args.file_to_export)
    deduplicated_rows = deduplicate(
        input_rows,
        existing_rows,
    )

    num_rows_appended = append_rows(resource, list(deduplicated_rows))
    logger.info("Appended %d rows", num_rows_appended)


if __name__ == "__main__":
    main()
