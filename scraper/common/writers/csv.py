import csv
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel


def write_to_csv(
    items: Iterable[BaseModel],
    output_path: Path,
) -> None:
    """Append the given items to the specified file in CSV format

    The elements of items should all be instances of the same BaseModel subclass.
    """
    iterator = iter(items)
    try:
        item = next(iterator)
    except StopIteration:
        # Iterable is empty, so there's nothing to save
        return
    fields = tuple(type(item).model_fields.keys()) + tuple(
        type(item).model_computed_fields.keys()
    )

    with open(output_path, "a", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fields)
        if out.tell() == 0:
            # We're at the beginning of the file, so write the header
            writer.writeheader()
        # Write the first item we popped from the iterable
        writer.writerow(item.model_dump())
        # Write the rest of the items
        for item in iterator:
            writer.writerow(item.model_dump())
