"""Parses the command-line arguments for the reporting module.

This is the entry-point component (``CLIParser`` in ``Design.md``): the only
place that reads the program's command-line arguments. It accepts two
positional arguments — the path to the log file to analyze and the log type
(e.g. ``Apache``) — validates them, and returns them as a typed
:class:`CLIArguments` model for the rest of the pipeline to consume.
"""
import argparse
from pathlib import Path

from pydantic import BaseModel


class CLIArguments(BaseModel):
    """The validated command-line arguments."""

    file_path: Path
    log_type: str


class CLIParser:
    """Builds and runs the command-line argument parser."""

    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(
            description="Produce a percentage breakdown of web-server log "
            "requests by Country, OS and Browser.",
        )
        self._parser.add_argument(
            "file_path",
            type=self._existing_file,
            help="path to the log file to analyze",
        )
        self._parser.add_argument(
            "log_type",
            help='the log format, e.g. "Apache"',
        )

    def parse(self, argv: list[str] | None = None) -> CLIArguments:
        """Parse ``argv`` (or ``sys.argv`` when ``None``) into typed arguments.

        Exits the process with a usage message if an argument is missing or the
        file path does not point to an existing file.
        """
        namespace = self._parser.parse_args(argv)
        return CLIArguments(file_path=namespace.file_path, log_type=namespace.log_type)

    def _existing_file(self, value: str) -> Path:
        """Argparse type that accepts only a path to an existing file."""
        path = Path(value)
        if not path.is_file():
            raise argparse.ArgumentTypeError(f"no such file: {value}")
        return path
