"""Extracts the OS and Browser dimensions from a log line's User-Agent field.

A single User-Agent string carries both pieces of information, so this one
extractor populates two dimensions at once. Parsing is delegated to the
``ua-parser`` library, whose regex database recognises the full variety of
browsers, operating systems and bots that appear in real access logs.
"""

from ua_parser import parse

from src.dimensions.dimension_extractor import DimensionExtractor
from src.dimensions.enums import DimensionName

# Position of the quoted User-Agent string within a parsed Apache combined-log
# line (the final field, after the referer).
_DEFAULT_USER_AGENT_FIELD_INDEX = 8


class UserAgentExtractor(DimensionExtractor):
    """Resolves OS and Browser names from the User-Agent field of a log line."""

    def __init__(self, user_agent_field_index: int = _DEFAULT_USER_AGENT_FIELD_INDEX) -> None:
        self._user_agent_field_index = user_agent_field_index
        # UA string -> {OS, Browser} cache. ua-parser runs a sizeable regex set
        # per call; the log repeats the same UA strings heavily (a few hundred
        # distinct values across thousands of lines), so caching avoids re-parsing.
        self._user_agent_to_dimensions: dict[str, dict[DimensionName, str | None]] = {}

    def extract(self, fields: list[str]) -> dict[DimensionName, str | None]:
        """Return ``{OS: ..., Browser: ...}`` for the line's User-Agent string.

        Either value is None when the User-Agent field is missing or the library
        cannot identify that dimension (e.g. a bot with no recognisable OS).
        """
        if self._user_agent_field_index >= len(fields):
            return {DimensionName.OS: None, DimensionName.BROWSER: None}
        user_agent = self._strip_quotes(fields[self._user_agent_field_index])
        if user_agent not in self._user_agent_to_dimensions:
            self._user_agent_to_dimensions[user_agent] = self._parse(user_agent)
        return self._user_agent_to_dimensions[user_agent]

    def _parse(self, user_agent: str) -> dict[DimensionName, str | None]:
        """Parse a raw User-Agent string into its OS and Browser family names."""
        result = parse(user_agent)
        os_family = result.os.family if result.os is not None else None
        browser_family = result.user_agent.family if result.user_agent is not None else None
        return {DimensionName.OS: os_family, DimensionName.BROWSER: browser_family}

    def _strip_quotes(self, field: str) -> str:
        """Drop the surrounding double quotes the log separator keeps on fields."""
        if len(field) >= 2 and field.startswith('"') and field.endswith('"'):
            return field[1:-1]
        return field
