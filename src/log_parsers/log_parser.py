from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from src.dimensions.enums import DimensionName


@dataclass
class Dimension:
    line_pos: int



class LogParser(ABC):

    def __init__(self, dimensions: dict[DimensionName, Any]):
        self.dimensions = dimensions

    def extract_fields_for_dimensions(self, line: list[str]) -> dict[str, str]:
        ...

