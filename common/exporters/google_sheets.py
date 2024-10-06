import argparse
import csv
import json
import logging
import os
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Sequence, Tuple

import dotenv
from googleapiclient.discovery import build, Resource
from google.oauth2.service_account import Credentials


# Columns (0-index) to use identify rows and detect duplicates
COLUMNS_FOR_DEDUPLICATION = (0, 1)


def load_environment_variable(variable_name: str) -> str:
    value = os.getenv(variable_name)
    if not value:
        raise ValueError(
            f"{variable_name} not found in .env file. "
            "Please see .env.example for the expected format."
        )
    return value


def connect(key_info: Mapping[str, str]) -> Resource:
    credentials = Credentials.from_service_account_info(
        key_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=credentials)


def load_csv(path: Path) -> Iterable[List[Any]]:
    with open(path, newline="") as file:
        yield from csv.reader(file)


def fetch_rows(
    resource: Resource,
    spreadsheet_id: str,
    sheet_name: str,
) -> List[List[Any]]:
    existing_values = resource.spreadsheets().values()
    request = existing_values.get(
        spreadsheetId=spreadsheet_id,
        range=sheet_name,
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
    spreadsheet_id: str,
    sheet_name: str,
    rows: List[List[Any]],
) -> int:
    body = {"values": rows}
    existing_values = resource.spreadsheets().values()
    request = existing_values.append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
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
        "file_to_export",
        type=Path,
        help="CSV file to export to Google Sheets",
    )
    parser.add_argument(
        "--no-dot-env",
        action="store_true",
        help="""
        Do not try to load configuration from .env file. Instead assume environment
        variables have already been set. Useful for automation.
        """,
    )
    args = parser.parse_args()

    logging.basicConfig(
        handlers=(
            logging.StreamHandler(),
            logging.FileHandler("log.txt", mode="a"),
        ),
        style="{",
        format="{asctime:s} {levelname:7s} {name:s}:{lineno:d} {message:s}",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=logging.DEBUG,
    )
    logger = logging.getLogger(__name__)

    if not args.no_dot_env:
        if not dotenv.load_dotenv():
            raise RuntimeError(
                "No .env file found. Please copy and modify .env.example following the "
                "instructions in README.md."
            )

    key_str = load_environment_variable("GOOGLE_SERVICE_ACCOUNT_KEY")
    try:
        key_info = json.loads(key_str)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Google Service Account key has invalid format. "
            "Please see .env.example for the expected format."
        ) from error
    spreadsheet_id = load_environment_variable("GOOGLE_SPREADSHEET_ID")
    sheet_name = load_environment_variable("GOOGLE_SHEET_NAME")

    resource = connect(key_info)
    existing_rows = fetch_rows(
        resource=resource,
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name,
    )
    logger.info("Fetched %d rows", len(existing_rows))
    input_rows = load_csv(args.file_to_export)
    deduplicated_rows = deduplicate(
        input_rows,
        existing_rows,
    )

    num_rows_appended = append_rows(
        resource=resource,
        spreadsheet_id=spreadsheet_id,
        sheet_name=sheet_name,
        rows=list(deduplicated_rows),
    )
    logger.info("Appended %d rows", num_rows_appended)


if __name__ == "__main__":
    main()
