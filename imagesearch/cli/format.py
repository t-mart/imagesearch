"""Enumeration of formats."""
from __future__ import annotations

from enum import Enum, auto
from typing import Dict

from imagesearch.exceptions import UnknownFormatException


class Format(Enum):
    """Formats for output."""

    TEXT = auto()
    JSON = auto()

    @classmethod
    def from_name(cls, name: str) -> Format:
        """Returns an format by name."""
        name_map: Dict[str, Format] = {
            format_.name.lower(): format_ for format_ in list(Format)
        }
        name_normalized = name.lower()
        if name_normalized not in name_map:
            raise UnknownFormatException(f"No format with name {name}")
        return name_map[name_normalized]

    @classmethod
    def supported_names(cls) -> str:
        """Returns a comma-separated string of all the format names."""
        return ", ".join(format_.name.lower() for format_ in list(Format))
