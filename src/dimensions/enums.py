from enum import Enum


class DimensionName(str, Enum):
    """Names of dimensions that can be extracted from log lines."""
    COUNTRY = "country"
    OS = "os"
    BROWSER = "browser"

