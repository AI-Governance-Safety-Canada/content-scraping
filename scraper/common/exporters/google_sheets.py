import argparse
import csv
import json
import logging
import os
from pathlib import Path
from typing import Any, cast, Iterable, List, Mapping, Sequence, Tuple

import dotenv
from googleapiclient.discovery import build, Resource  # type: ignore[import-untyped]
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
    )  # type: ignore[no-untyped-call]
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
    return cast(List[List[Any]], result.get("values", []))


def compare_headers(
    new_rows: Sequence[List[Any]],
    existing_rows: Sequence[List[Any]],
) -> None:
    logger = logging.getLogger(__name__)
    if not new_rows or not existing_rows:
        logger.debug("No headers to compare")
        return
    if new_rows[0] == existing_rows[0]:
        logger.debug("Headers match")
        return
    logger.error("Headers do not match")
    logger.info("Existing headers: %s", existing_rows[0])
    logger.info("New headers:      %s", new_rows[0])
    raise RuntimeError("Headers in new and existing tables do not match")


def deduplicate(
    new_rows: Iterable[List[Any]],
    existing_rows: Iterable[List[Any]],
    columns_to_use: Sequence[int] = COLUMNS_FOR_DEDUPLICATION,
) -> Iterable[List[Any]]:
    logger = logging.getLogger(__name__)

    def is_substring(field_a: str, field_b: str) -> bool:
        return (
            field_a.lower() in field_b.lower()
            or field_b.lower() in field_a.lower()
        )

    seen_rows = list(existing_rows)
    for new_row in new_rows:
        for seen_row in seen_rows:
            if all(is_substring(new_row[col], seen_row[col]) for col in columns_to_use):
                logger.debug("Skipping duplicate row: %s", new_row)
                break
        else:
            seen_rows.append(new_row)
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
    return cast(int, result.get("updates", {}).get("updatedRows", 0))


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
    input_rows = list(load_csv(args.file_to_export))
    compare_headers(input_rows, existing_rows)

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
