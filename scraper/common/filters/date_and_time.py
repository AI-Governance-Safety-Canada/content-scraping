from datetime import date
from typing import cast, Callable, Iterable, Optional, TypeVar

T = TypeVar("T")


def exclude_old_items(
    items: Iterable[T],
    cutoff: Optional[date] = None,
    *,
    key: Optional[Callable[[T], date]] = None,
    attribute: Optional[str] = None,
) -> Iterable[T]:
    """Exclude items from before the cutoff date

    To convert each item to a date, provide either
        1.  A callable key which takes an item and returns the date to check
        2.  A string attribute of the item

    If cuttoff is unspecified or None, use the present date.
    """
    if (key, attribute).count(None) != 1:
        raise TypeError("Must specify one of key and attribute")

    if cutoff is None:
        # Use current local time
        cutoff = date.today()

    if key is None:
        # The above check should guarantee that attribute is not None here.
        # But an explicit assert makes mypy happy.
        assert attribute is not None

        def key(item: T) -> date:
            return cast(date, getattr(item, attribute))

    def keep(item: T) -> bool:
        return key(item) >= cutoff

    return filter(keep, items)
