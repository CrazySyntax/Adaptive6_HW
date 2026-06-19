from abc import ABC, abstractmethod

from src.line_separators.log_line_separator import LogLineSeparator

# Characters that open a group within which whitespace does not split a field.
# Maps each opening character to its matching closing character.
_GROUP_DELIMITERS = {'"': '"', "[": "]"}

class ApacheLogLineSeparator(LogLineSeparator):

    def parse_line(self, line: str) -> list[str]:
        """Split a single log line into its fields.

        Whitespace separates fields except inside a ``"..."`` or ``[...]`` group,
        whose contents (including the delimiters) are kept as one field.
        """
        fields: list[str] = []
        current: list[str] = []
        closing_char: str | None = None  # set while inside a quoted/bracketed group

        for char in line:
            if closing_char is not None:
                # Inside a group: append everything until the matching close.
                current.append(char)
                if char == closing_char:
                    closing_char = None
            elif char in _GROUP_DELIMITERS:
                closing_char = _GROUP_DELIMITERS[char]
                current.append(char)
            elif char.isspace():
                if current:
                    fields.append("".join(current))
                    current = []
            else:
                current.append(char)

        if current:
            fields.append("".join(current))
        return fields