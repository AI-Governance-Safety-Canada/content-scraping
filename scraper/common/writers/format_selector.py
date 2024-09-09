from pathlib import Path
from typing import Any, Iterable

from .csv import write_to_csv
from .jsonl import write_to_jsonl


SUPPORTED_FORMATS = {
    ".csv": write_to_csv,
    ".jsonl": write_to_jsonl,
}


def write_items(
    items: Iterable[Any],
    output_path: Path,
) -> None:
    """Append the given items to the specified file

    Infer the file format from the extension. If the extension isn't supported, throw an exception.

    The elements of items should all be instances of the same dataclass.
    """
    extension = output_path.suffix.lower()
    try:
        writer = SUPPORTED_FORMATS[extension]
    except KeyError:
        raise ValueError(f"Unsupported file type: {extension}")
    return writer(items, output_path)
