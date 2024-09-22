import argparse
import csv
import logging
from pathlib import Path
from typing import Any, Iterable, List

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


# The ID and range of the target spreadsheet.
SPREADSHEET_ID = "1ZNIRMp2ra8yo6GJSX2wDFSjsdDMQu7o-173ue-zQsm0"
RANGE_NAME = "Sheet1!A1"


def authenticate(credentials_path: Path) -> Credentials:
    return Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )


def load_csv(path: Path) -> Iterable[List[Any]]:
    with open(path, newline="") as file:
        yield from csv.reader(file)


def append_rows(
    credentials: Credentials,
    rows: List[List[Any]],
) -> int:
    resource = build("sheets", "v4", credentials=credentials)
    body = {"values": rows}
    existing_values = resource.spreadsheets().values()
    request = existing_values.append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
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

    credentials = authenticate(args.credentials_file)
    rows = list(load_csv(args.file_to_export))
    num_rows_appended = append_rows(credentials, rows)
    logger.info("Appended %d rows", num_rows_appended)


if __name__ == "__main__":
    main()
