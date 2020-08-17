"""Test commands."""
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
from functools import partial

import imagehash
import numpy
import pytest

from imagesearch import Algorithm, ImageDiff, Dupe
from imagesearch.cli.command import CompareCommand, DupeCommand, Command
from imagesearch.cli.format import Format
from imagesearch.exceptions import UnknownFormatException


def test_dupe_json_command(capsys) -> None:  # type: ignore
    """
    Test that dupe command is called correctly.

    The call will also be with json format, so ensure the output is a JSON document with the right
    structure.
    """
    search_paths = [Path("foo/bar"), Path("lol/123")]
    algorithm = Algorithm.DHASH
    format_ = Format.JSON

    namespace = Namespace(
        search_paths=search_paths, algorithm=algorithm, format=format_,
    )

    with patch("imagesearch.cli.command.Dupe") as mock_dupe:
        # setup
        mock_dupe.find.return_value = iter(
            [
                Dupe(
                    image_hash=imagehash.ImageHash(
                        numpy.array([True, False, True, False])
                    ),
                    algorithm=algorithm,
                    paths=set([Path("foo/bar/img.jpg"), Path("lol/123/img.jpg"),]),
                ),
            ]
        )

        # run
        DupeCommand.run(namespace)

        # verify
        mock_dupe.find.assert_called_once_with(
            search_paths=search_paths, algorithm=algorithm
        )

    # verify json structure
    capjson = json.loads(capsys.readouterr().out)

    assert capjson["algorithm"] == algorithm.algo_name  # pylint: disable=no-member
    assert len(capjson["dupes"]) == 1

    json_dupe = capjson["dupes"][0]
    assert set(json_dupe.keys()) == set(["image_hash", "paths"])


def test_compare_json_command(capsys) -> None:  # type: ignore
    """
    Test that compare command is called correctly.

    The call will also be with json format, so ensure the output is a JSON document with the right
    structure.
    """
    ref_path = Path("ref/img")
    search_paths = [Path("foo/bar"), Path("lol/123")]
    algorithm = Algorithm.DHASH
    threshold = 123
    stop_on_first_match = True
    format_ = Format.JSON

    namespace = Namespace(
        ref_path=ref_path,
        search_paths=search_paths,
        algorithm=algorithm,
        threshold=threshold,
        stop_on_first_match=stop_on_first_match,
        format=format_,
    )

    with patch("imagesearch.cli.command.ImageDiff") as mock_image_diff:
        # setup
        mock_image_diff.compare.return_value = iter(
            [ImageDiff(path=Path("foo/bar/img.jpg"), diff=5),]
        )

        # run
        CompareCommand.run(namespace)

        # verify
        mock_image_diff.compare.assert_called_once_with(
            ref_path=ref_path,
            search_paths=search_paths,
            algorithm=algorithm,
            threshold=threshold,
            stop_on_first_match=stop_on_first_match,
        )

    # verify json structure
    capjson = json.loads(capsys.readouterr().out)

    assert capjson["reference_path"] == str(ref_path.resolve())
    assert capjson["algorithm"] == algorithm.algo_name  # pylint: disable=no-member
    assert len(capjson["diffs"]) == 1

    json_diff = capjson["diffs"][0]
    assert set(json_diff.keys()) == set(["path", "diff"])


def test_dupe_text_output() -> None:
    """
    Tests that dupe text output is built.

    Since the text format is not designed to be machine-readable, this test doesn't test the format.
    """
    search_paths = [Path("foo/bar"), Path("lol/123")]
    algorithm = Algorithm.DHASH
    format_ = Format.TEXT

    namespace = Namespace(
        search_paths=search_paths, algorithm=algorithm, format=format_,
    )

    with patch("imagesearch.cli.command.Dupe") as mock_dupe:
        # setup
        mock_dupe.find.return_value = iter(
            [
                Dupe(
                    image_hash=imagehash.ImageHash(
                        numpy.array([True, False, True, False])
                    ),
                    algorithm=algorithm,
                    paths=set([Path("foo/bar/img.jpg"), Path("lol/123/img.jpg"),]),
                ),
            ]
        )
        DupeCommand.text_output = MagicMock(return_value="")  # type: ignore

        # run
        DupeCommand.run(namespace)

        # verify
        mock_dupe.find.assert_called_once_with(
            search_paths=search_paths, algorithm=algorithm
        )
        DupeCommand.text_output.assert_called_once_with(  # pylint: disable=no-member
            args=namespace, items=mock_dupe.find.return_value
        )


def test_compare_text_output() -> None:
    """
    Tests that compare text output is built.

    Since the text format is not designed to be machine-readable, this test doesn't test the format.
    """
    ref_path = Path("ref/img")
    search_paths = [Path("foo/bar"), Path("lol/123")]
    algorithm = Algorithm.DHASH
    threshold = 123
    stop_on_first_match = True
    format_ = Format.TEXT

    namespace = Namespace(
        ref_path=ref_path,
        search_paths=search_paths,
        algorithm=algorithm,
        threshold=threshold,
        stop_on_first_match=stop_on_first_match,
        format=format_,
    )

    with patch("imagesearch.cli.command.ImageDiff") as mock_image_diff:
        # setup
        mock_image_diff.compare.return_value = iter(
            [ImageDiff(path=Path("foo/bar/img.jpg"), diff=5),]
        )
        CompareCommand.text_output = MagicMock(return_value="")  # type: ignore

        # run
        CompareCommand.run(namespace)

        # verify
        mock_image_diff.compare.assert_called_once_with(
            ref_path=ref_path,
            search_paths=search_paths,
            algorithm=algorithm,
            threshold=threshold,
            stop_on_first_match=stop_on_first_match,
        )
        CompareCommand.text_output.assert_called_once_with(  # pylint: disable=no-member
            args=namespace, items=mock_image_diff.compare.return_value
        )


def test_output_function_by_format_throws() -> None:
    """
    Tests that an unknown format throwns an UnknownFormatException.

    This is a little redundant with mypy typing enforcement.
    """
    with pytest.raises(UnknownFormatException):
        DupeCommand.output_function_by_format("bogus")  # type: ignore


def test_abstract_command_methods_throw_exception() -> None:
    """
    Tests that one cannot call abstract methods of Command.
    """
    partial_methods = [
        partial(Command._generate, None),  # pylint: disable=protected-access
        partial(Command.json_output, None, None),
        partial(Command.text_output, None, None),
    ]
    for partial_method in partial_methods:
        with pytest.raises(NotImplementedError):
            partial_method()  # type: ignore
