import dataclasses
import json
from pathlib import Path
from typing import Any, Iterable


def write_to_jsonl(
    items: Iterable[Any],
    output_path: Path,
) -> None:
    """Append the given items to the specified file in JSON Lines format

    The elements of items should all be instances of the same dataclass.
    """
    with open(output_path, "a", encoding="utf-8") as out:
        for item in items:
            line = json.dumps(
                dataclasses.asdict(item),
                separators=(",", ":"),
                default=str,
            )
            out.write(line)
            out.write("\n")
