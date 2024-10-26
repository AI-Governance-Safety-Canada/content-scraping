from abc import abstractmethod, ABC
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel


LeanResponse = Dict[str, List[Dict[Any, Any]]]
RichResponse = TypeVar("RichResponse", bound=BaseModel)
ApiResponse = Optional[Union[LeanResponse | RichResponse]]


class Api(ABC, Generic[RichResponse]):
    @abstractmethod
    def scrape(self, url: str) -> ApiResponse[RichResponse]: ...
