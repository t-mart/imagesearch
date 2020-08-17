"""Test commands."""
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch
import json

import imagehash
import numpy

from imagesearch import Algorithm, ImageDiff, Dupe
from imagesearch.cli.command import CompareCommand, DupeCommand
from imagesearch.cli.format import Format

def test_dupe_command(capsys) -> None:  # type: ignore
    """
    Test that dupe command is called correctly.

    The call will also be with json format, so ensure the output is a JSON document with the right
    structure.
    """
    search_paths = [Path("foo/bar"), Path('lol/123')]
    algorithm = Algorithm.DHASH
    format_ = Format.JSON

    namespace = Namespace(
        search_paths=search_paths,
        algorithm=algorithm,
        format=format_,
    )

    with patch('imagesearch.cli.command.Dupe') as mock_dupe:
        mock_dupe.find.return_value = iter([
            Dupe(
                image_hash=imagehash.ImageHash(numpy.array([True, False, True, False])),
                algorithm=algorithm,
                paths=set([
                    Path("foo/bar/img.jpg"),
                    Path("lol/123/img.jpg"),
                ])
            ),
        ])

        DupeCommand.run(namespace)

        mock_dupe.find.assert_called_once_with(
            search_paths=search_paths,
            algorithm=algorithm
        )

    capjson = json.loads(capsys.readouterr().out)

    assert capjson["algorithm"] == algorithm.algo_name  # pylint: disable=no-member
    assert len(capjson["dupes"]) == 1

    json_dupe = capjson["dupes"][0]
    assert set(json_dupe.keys()) == set(["image_hash", "paths"])

def test_compare_command(capsys) -> None:  # type: ignore
    """
    Test that compare command is called correctly.

    The call will also be with json format, so ensure the output is a JSON document with the right
    structure.
    """
    ref_path = Path('ref/img')
    search_paths = [Path("foo/bar"), Path('lol/123')]
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

    with patch('imagesearch.cli.command.ImageDiff') as mock_image_diff:
        mock_image_diff.compare.return_value = iter([
            ImageDiff(path=Path("foo/bar/img.jpg"), diff=5),
        ])

        CompareCommand.run(namespace)

        mock_image_diff.compare.assert_called_once_with(
            ref_path=ref_path,
            search_paths=search_paths,
            algorithm=algorithm,
            threshold=threshold,
            stop_on_first_match=stop_on_first_match
        )

    capjson = json.loads(capsys.readouterr().out)

    assert capjson["reference_path"] == str(ref_path.resolve())
    assert capjson["algorithm"] == algorithm.algo_name  # pylint: disable=no-member
    assert len(capjson["diffs"]) == 1

    json_diff = capjson["diffs"][0]
    assert set(json_diff.keys()) == set(["path", "diff"])
