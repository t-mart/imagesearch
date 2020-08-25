"""
Tests the CLI parser.

I don't usually see any ArgumentParser configuration testing in other projects. It'd also be quite
exhaustive to write unit tests for each argument (defaults, type conversions, etc). The
configuration is the spec. So, that's not really the focus of this file. It's more to test the
functions that I've written.
"""

import pytest

from imagesearch import Algorithm
from imagesearch.cli import PARSER
from imagesearch.exceptions import CLIException, BadAlgoParamsException
from tests.fixtures import TEST_IMAGE_DIR

WHASH = Algorithm.WHASH


def test_subcommand_not_provided() -> None:
    """Tests that an exception is raised when there's no subcommand provided."""
    with pytest.raises(CLIException):
        PARSER.parse_args([])


def test_subcommand_invalid() -> None:
    """Tests that an exception is raise when the subcommand is wrong."""
    with pytest.raises(CLIException):
        PARSER.parse_args(["bogus_subcommand"])


def test_parser_algo_params_not_given() -> None:
    """Tests that the algorithm argument parsing works when no argument is given."""
    default_algo_params_map = {
        param.name: param.default_value
        for param in WHASH.params  # pylint: disable=no-member
    }
    args = [
        "dupe",
        str(TEST_IMAGE_DIR),
        "--whash",
    ]

    parsed_args = PARSER.parse_args(args=args)
    algo_params = parsed_args.algo_params

    for arg_name, default_arg_value in default_algo_params_map.items():
        assert algo_params[arg_name] == default_arg_value


def test_parser_algo_params_single() -> None:
    """Tests that the algorithm argument parsing works when a single argument is given."""
    default_algo_params_map = {
        param.name: param.default_value
        for param in WHASH.params  # pylint: disable=no-member
    }
    args = [
        "dupe",
        str(TEST_IMAGE_DIR),
        "--whash",
        "--algo-params",
        "hash_size=10",
    ]

    parsed_args = PARSER.parse_args(args=args)
    algo_params = parsed_args.algo_params

    assert algo_params["hash_size"] == 10
    assert algo_params["image_scale"] == default_algo_params_map["image_scale"]
    assert algo_params["mode"] == default_algo_params_map["mode"]
    assert (
        algo_params["remove_max_haar_ll"]
        == default_algo_params_map["remove_max_haar_ll"]
    )


def test_parser_algo_params_nothing_is_false() -> None:
    """
    Tests that the algorithm argument parsing works when a single argument is given with a name and
    equals sign, but no value, and it's a bool conversion. i.e. "remove_max_haar_ll=" should set it
    to False.
    """
    default_algo_params_map = {
        param.name: param.default_value
        for param in WHASH.params  # pylint: disable=no-member
    }
    args = [
        "dupe",
        str(TEST_IMAGE_DIR),
        "--whash",
        "--algo-params",
        "remove_max_haar_ll=",
    ]

    parsed_args = PARSER.parse_args(args=args)
    algo_params = parsed_args.algo_params

    assert algo_params["hash_size"] == default_algo_params_map["hash_size"]
    assert algo_params["image_scale"] == default_algo_params_map["image_scale"]
    assert algo_params["mode"] == default_algo_params_map["mode"]
    assert algo_params["remove_max_haar_ll"] is False


def test_parser_algo_params_multiple() -> None:
    """
    Tests that the algorithm argument parsing works when all arguments are overridden. This pretty
    much runs a combination of the above tests, but ensure there's no strange side effects.
    """
    args = [
        "dupe",
        str(TEST_IMAGE_DIR),
        "--whash",
        "--algo-params",
        "image_scale=32,remove_max_haar_ll=,hash_size=10,mode=db4",
    ]

    parsed_args = PARSER.parse_args(args=args)
    algo_params = parsed_args.algo_params

    assert algo_params["hash_size"] == 10
    assert algo_params["image_scale"] == 32
    assert algo_params["mode"] == "db4"
    assert algo_params["remove_max_haar_ll"] is False


def test_parser_algo_params_no_equals() -> None:
    """
    Tests that the algorithm argument parsing works when all arguments are overridden. This pretty
    much runs a combination of the above tests, but ensure there's no strange side effects.
    """
    args = [
        "dupe",
        str(TEST_IMAGE_DIR),
        "--whash",
        "--algo-params",
        "image_scale",
    ]

    with pytest.raises(BadAlgoParamsException):
        PARSER.parse_args(args=args)


def test_parser_algo_params_invalid_arg_name() -> None:
    """
    Tests that the algorithm argument parsing works when all arguments are overridden. This pretty
    much runs a combination of the above tests, but ensure there's no strange side effects.
    """
    args = [
        "dupe",
        str(TEST_IMAGE_DIR),
        "--whash",
        "--algo-params",
        "life=42",
    ]

    with pytest.raises(BadAlgoParamsException):
        PARSER.parse_args(args=args)


def test_parser_algo_params_bad_type() -> None:
    """
    Tests that the algorithm argument parsing works when all arguments are overridden. This pretty
    much runs a combination of the above tests, but ensure there's no strange side effects.
    """
    args = [
        "dupe",
        str(TEST_IMAGE_DIR),
        "--whash",
        "--algo-params",
        "image_scale=foo",
    ]

    with pytest.raises(BadAlgoParamsException):
        PARSER.parse_args(args=args)
