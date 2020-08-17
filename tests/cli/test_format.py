"""Test the format enum"""
import pytest

from imagesearch.cli.format import Format
from imagesearch.exceptions import UnknownFormatException

def test_invalid_format_from_name() -> None:
    """Tests that an invalid format to Format.from_name raises an exception."""
    with pytest.raises(UnknownFormatException):
        Format.from_name("bogus")

def test_valid_format_from_name() -> None:
    """Tests all valid formats to Format.from_name."""
    assert Format.from_name("json").name == "JSON"
    assert Format.from_name("text").name == "TEXT"
