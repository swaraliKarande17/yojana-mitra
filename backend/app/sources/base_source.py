from abc import ABC, abstractmethod
from typing import Any


class GovernmentSource(ABC):
    """
    Base interface for trusted government data sources.
    """

    source_name: str
    authority: str

    @abstractmethod
    async def fetch_schemes(self) -> list[dict[str, Any]]:
        """
        Fetch scheme records from the official source.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw_item: dict[str, Any]) -> dict[str, Any]:
        """
        Convert source-specific data into Yojana Mitra's internal schema.
        """
        raise NotImplementedError