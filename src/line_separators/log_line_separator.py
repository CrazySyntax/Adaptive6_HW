from abc import ABC, abstractmethod


class LogLineSeparator(ABC):
    """Interface for log line separators that parse a log line into its components."""

    @abstractmethod
    def parse_line(self, line: str) -> list[str]:
        """Separate a log line into its components and return them as a dictionary."""
        ...