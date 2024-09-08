import csv
import dataclasses
from pathlib import Path
from typing import Any, Iterable


def write_to_csv(
    items: Iterable[Any],
    output_path: Path,
) -> None:
    """Append the given items to the specified file in CSV format

    The elements of items should all be instances of the same dataclass.
    """
    iterator = iter(items)
    try:
        item = next(iterator)
    except StopIteration:
        # Iterable is empty, so there's nothing to save
        return
    fields = tuple(field.name for field in dataclasses.fields(item))

    with open(output_path, "a", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fields)
        if out.tell() == 0:
            # We're at the beginning of the file, so write the header
            writer.writeheader()
        writer.writerow(dataclasses.asdict(item))
        for item in iterator:
            writer.writerow(dataclasses.asdict(item))
