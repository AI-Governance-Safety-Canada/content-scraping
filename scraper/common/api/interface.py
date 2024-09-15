from abc import abstractmethod, ABC
from typing import Any, Dict, List, Optional


ApiResponse = Optional[Dict[str, List[Dict[Any, Any]]]]


class API(ABC):
    @abstractmethod
    def scrape(self, url: str) -> ApiResponse: ...
