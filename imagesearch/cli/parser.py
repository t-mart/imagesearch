"""Definition of the argument parser."""
from pathlib import Path
import argparse
from typing import NoReturn

from .. import __version__
from ..fingerprint import Algorithm
from ..exceptions import CLIException
from .command import DupeCommand, CompareCommand, Format

def _add_algo_arg_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    All subcommands of imagesearch take an optional algorithm option. This helper method allows us
    to avoid repeating ourselves.
    """
    parser.add_argument(
        "-a",
        "--algorithm",
        action="store",
        default=Algorithm.AHASH,
        type=Algorithm.from_name,
        help=f"""
        The algorithm to use to fingerprint the images. See the imagehash library for documentation
        on how each works. {Algorithm.all_descriptions()}.
        """
    )


def _add_format_arg_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    All subcommands of imagesearch take an optional format option. This helper method allows us
    to avoid repeating ourselves.
    """
    parser.add_argument(
        "-f",
        "--format",
        action="store",
        default=Format.JSON,
        type=Format.from_name,
        help=f"""
        The format to output results in. Choose from among: {Format.supported_names()}.
        """
    )

class ImageSearchArgumentParser(argparse.ArgumentParser):
    """Arg parser with customized error handling."""
    def error(self, message: str) -> NoReturn:
        """Raises a CLIException."""
        raise CLIException(message)


PARSER = ImageSearchArgumentParser(
    prog="imagesearch",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="""
    Performs various visual matching operations on images.
    """,
)

PARSER.add_argument(
    "--version",
    action="version",
    version=__version__
)

_SUBCOMMAND_PARSER = PARSER.add_subparsers(
    dest="subcommand",
    required=True,
)

_COMPARE_PARSER = _SUBCOMMAND_PARSER.add_parser(
    "compare",
    help="""
    Compares a reference image to other images and returns a measure of visual similarity.
    """
)

_COMPARE_PARSER.add_argument(
    "ref_path",
    type=Path,
    metavar="REF_PATH",
    default=None,
    help="""
    The reference image to compare among the search paths.
    """
)

_COMPARE_PARSER.add_argument(
    "search_paths",
    nargs="+",
    metavar="SEARCH_PATH",
    type=Path,
    help="""
    The path(s) of other images to compare against the reference image. This argument may be
    supplied multiples times. The path may be either a file (for explicit comparison) or a directory
    that will be recursively searched for image files.
    """
)

_add_algo_arg_to_parser(_COMPARE_PARSER)
_add_format_arg_to_parser(_COMPARE_PARSER)

_COMPARE_PARSER.set_defaults(command=CompareCommand.run)

_COMPARE_PARSER.add_argument(
    "-1",
    "--stop-on-first-match",
    action="store_true",
    help="""
    Stop searching immediately after the first image with diff <= threshold is found
    (instead of continuing to search through all search paths), which also means that
    this argument must be used with the threshold argument as well . If multiple
    matches do exist, the result is arbitrary. This argument is intended to search
    through a large set of images where only a single image is desired.
    """
)

_COMPARE_PARSER.add_argument(
    "-t",
    "--threshold",
    type=int,
    default=None,
    help="""
    The the maximum difference at which to consider 2 images as a match. Lower numbers mean closer
    match. This value is subjective and depends on the hash algorithm used, so testing without a
    threshold may be useful to feel for the values. Omit to use an infinite threshold.
    """
)

_DUPE_PARSER = _SUBCOMMAND_PARSER.add_parser(
    "dupe",
    help="""
    Finds images which hash to the same value within the given paths.
    """
)

_DUPE_PARSER.add_argument(
    "search_paths",
    nargs="+",
    metavar="SEARCH_PATH",
    type=Path,
    help="""
    The path(s) to search for visually similar images. This argument may be supplied
    multiples times. The path may be either a file (for explicit comparison) or a
    directory that will be recursively searched for image files.
    """
)

_add_algo_arg_to_parser(_DUPE_PARSER)
_add_format_arg_to_parser(_DUPE_PARSER)

_DUPE_PARSER.set_defaults(command=DupeCommand.run)
