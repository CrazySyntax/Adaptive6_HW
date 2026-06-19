"""Interface for extracting a single dimension value from a parsed log line."""

from abc import ABC, abstractmethod


class DimensionExtractor(ABC):
    """Extracts one dimension's value from a parsed log line.

    A parsed log line is the list of fields produced by ``FileParser`` (e.g.
    IP address, timestamp, request, status). Each concrete extractor knows
    which field(s) it needs and how to turn them into a reportable value
    (e.g. Country, OS, Browser).
    """

    @abstractmethod
    def extract(self, fields: list[str]) -> str | None:
        """Return this dimension's value for ``fields``, or None if unresolved."""
        ...
