from typing import Any

from pydantic import BaseModel, field_validator


class NullStringValidator(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def null_string_to_none(cls, value: Any) -> Any:
        """Convert the string "null" to None

        The API can sometimes return the string "null" instead of the JSON value null.
        """
        if isinstance(value, str) and value.lower() == "null":
            return None
        return value
