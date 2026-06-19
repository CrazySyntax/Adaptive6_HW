"""Splits raw log lines into fields, treating quoted/bracketed groups as atomic.

A log line is whitespace-separated, except that whitespace inside double quotes
(``"..."``) or square brackets (``[...]``) does not split a field. For example,
in a standard Apache access-log line both ``[17/May/2015:10:05:24 +0000]`` and
``"GET /path HTTP/1.1"`` are single fields. The surrounding quotes/brackets are
kept as part of the field value.

The log file is treated as a table: every row must have the same number of
fields. The expected width is taken from the first parsed row (unless given
explicitly) and every subsequent row is validated against it.
"""

from pathlib import Path
from typing import Iterator

from src.line_separators.log_line_separator import LogLineSeparator


class FileParser:
    """Tokenizes log lines into equal-width rows of string fields."""

    def __init__(self, line_separator: LogLineSeparator) -> None:
        # If None, the width is inferred from the first row parsed by parse_file.
        self.line_separator = line_separator


    def parse_file(self, file_path: str | Path) -> Iterator[list[str]]:
        """Yield one list of fields per non-empty line in the file.

        Raises ValueError if a row's field count differs from the expected width
        (the first row's width when not set explicitly), since the log is
        expected to be a uniform table.
        """
        path = Path(file_path)

        with path.open(encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue

                yield self.line_separator.parse_line(line)
