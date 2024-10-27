import logging
from pathlib import Path
from typing import Iterable, List, Optional


def configure_logging(
    level: int = logging.DEBUG,
    filepath: Optional[Path] = Path("log.txt"),
) -> None:
    """Configure log level format and handlers

    This must be called before any loggers are created.
    """
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if filepath is not None:
        handlers.append(logging.FileHandler(filepath, mode="a"))
    logging.basicConfig(
        handlers=handlers,
        style="{",
        format="{asctime:s} {levelname:7s} {name:s}:{lineno:d} {message:s}",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=level,
    )


def set_log_level(
    level: int = logging.INFO,
    logger_names: Iterable[str] = (
        "httpcore",
        "httpx",
        "urllib3",
    ),
) -> None:
    """Set the log level for the given loggers

    This is helpful for silencing unhelpful logging from noisy libraries
    """
    for name in logger_names:
        logging.getLogger(name).setLevel(level)
