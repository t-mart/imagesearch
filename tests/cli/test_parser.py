"""
Tests the CLI parser.

I'm a bit on the fence with if these tests are necessary. I don't usually see any ArgumentParser
configuration testing in other projects. It'd also be quite exhaustive to write unit tests for each
argument (defaults, type conversions, etc). The configuration is the spec.
"""

import pytest

from imagesearch.cli import PARSER
from imagesearch.exceptions import CLIException

def test_subcommand_not_provided() -> None:
    """Tests that an exception is raised when there's no subcommand provided."""
    with pytest.raises(CLIException):
        PARSER.parse_args([])

def test_subcommand_invalid() -> None:
    """Tests that an exception is raise when the subcommand is wrong."""
    with pytest.raises(CLIException):
        PARSER.parse_args(["bogus_subcommand"])
