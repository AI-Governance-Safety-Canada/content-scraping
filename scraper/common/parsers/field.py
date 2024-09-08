from typing import Any, Dict, Optional, Type, TypeVar


T = TypeVar("T")


def fetch_field_with_type(
    dictionary: Dict[Any, Any],
    key: str,
    typ: Type[T],
) -> Optional[T]:
    """Fetch the value associated with the key if it has the given type.

    If the key is not present or the value has a different type, return None.
    """
    value = dictionary.get(key)
    if isinstance(value, typ):
        return value
    return None
