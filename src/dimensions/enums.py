from enum import Enum


class DimensionName(str, Enum):
    """Names of dimensions that can be extracted from log lines.

    Each member carries its internal ``value`` (used as a dict key throughout
    the pipeline) plus a human-readable ``label`` used as the report header.
    A new dimension declares both here and nothing else needs to change.
    """
    COUNTRY = ("country", "Country")
    OS = ("os", "OS")
    BROWSER = ("browser", "Browser")

    def __new__(cls, value: str, label: str) -> "DimensionName":
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member

