"""Interface for extracting dimension values from a parsed log line."""

from abc import ABC, abstractmethod

from src.dimensions.enums import DimensionName


class DimensionExtractor(ABC):
    """Extracts one or more dimension values from a parsed log line.

    A parsed log line is the list of fields produced by ``FileParser`` (e.g.
    IP address, timestamp, request, status). Each concrete extractor knows
    which field(s) it needs and how to turn them into reportable values
    (e.g. Country, OS, Browser).
    """

    @abstractmethod
    def extract(self, fields: list[str]) -> dict[DimensionName, str | None]:
        """Return a ``{DimensionName: value}`` mapping for ``fields``.

        An extractor declares which dimension(s) it produces via the keys, so a
        single extractor may populate several dimensions from one field (e.g. a
        user-agent extractor yielding both OS and Browser). Most extractors
        return a single entry (e.g. ``GeoIpExtractor`` returns just Country);
        ``None`` signals that nothing could be extracted.
        """
        ...
