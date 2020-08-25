"""Definition of the argument parser."""
from pathlib import Path
import argparse
from typing import NoReturn, Sequence, Optional, Text, Dict, Union

from imagesearch import __version__
from imagesearch.algo import Algorithm
from imagesearch.exceptions import CLIException, BadAlgoParamsException
from imagesearch.cli.command import DupeCommand, CompareCommand, Format


class ImageSearchArgumentParser(argparse.ArgumentParser):
    """Arg parser with customized parsing and error handling."""

    def parse_args(
        self,
        args: Optional[Sequence[Text]] = None,
        namespace=None,
    ):
        parsed, _ = super().parse_known_args(args=args, namespace=namespace)

        # turn the algorithm name into one of the enumeration members of Algorithm
        if not parsed.algorithm:
            parsed.algorithm = "dhash"
        parsed.algorithm = Algorithm.from_name(parsed.algorithm)

        # using the algorithm, parse any override to the default algorithm call.
        parsed.algo_params = self._parse_algo_params(
            params_str=parsed.algo_params,
            algorithm=parsed.algorithm
        )

        return parsed

    @staticmethod
    def _parse_algo_params(
        params_str: str,
        algorithm: Algorithm,
    ) -> Dict[str, Optional[Union[str, bool, int]]]:
        """
        Parse an argument string like
        "foo=1,bar=True,false_val=" where foo is an int and bar/false_val are bools
        into
        {"foo": 1, bar=True, false_val=False}.
        Then, update these arguments on top of the default argument dict. If args_str is falsy,
        just return the default argument dict.
        """
        # fill with default key-value pairs first
        parsed_params: Dict[str, Optional[Union[str, bool, int]]] = {
            arg.name: arg.default_value for arg in algorithm.params
        }
        if not params_str:
            return parsed_params

        # make another dict that maps arg names to the AlgorithmArg object
        args_by_name = {arg.name: arg for arg in algorithm.params}
        parts = [arg.strip() for arg in params_str.split(",")]

        for part in parts:
            try:
                name, value = part.split("=", maxsplit=1)
            except ValueError:
                raise BadAlgoParamsException(
                    "Each key-value pair in --algo-params must be separated by an equals sign (=)."
                )

            if name not in args_by_name:
                raise BadAlgoParamsException(
                    f"\"{name}\" is not an acceptable parameter name for algorithm "
                    f"{algorithm.algo_name}"
                )

            try:
                converted_value = args_by_name[name].converter(value)
            except ValueError as exc:
                raise BadAlgoParamsException(
                    f"Value \"{value}\" of parameter \"{name}\" cannot be converted to the correct "
                    f"type: {exc}"
                )

            parsed_params[name] = converted_value

        return parsed_params

    def error(self, message: str) -> NoReturn:
        """Raises a CLIException instead of exiting."""
        raise CLIException(message)


def _add_algo_params_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    All subcommands of imagesearch take an optional algorithm option. This helper method allows us
    to avoid repeating ourselves.
    """
    algo_group = parser.add_mutually_exclusive_group()

    for algo in list(Algorithm):
        params_help = ", ".join(
            f"{params.name} ({params.help} Default={params.default_value})"
            for params in algo.params
        ) + "."
        algo_group.add_argument(
            f"--{algo.algo_name}",
            action="store_const",
            const=algo.algo_name,
            dest="algorithm",
            help=f"""
            {algo.description} Available parameters: {params_help}
            """
        )

    parser.add_argument(
        "--algo-params",
        action="store",
        type=str,
        default="",
        help="""
        Provide additional parameters to the algorithms to modify how they run. Must be specified in
        the form "foo=1,bar=a_string". Commas are used to separate parameters. See help text for
        each algorithm to see available parameters.
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
        """,
    )


PARSER = ImageSearchArgumentParser(
    prog="imagesearch",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="""
    Performs various visual matching operations on images.
    """,
)

PARSER.add_argument("--version", action="version", version=__version__)

_SUBCOMMAND_PARSER = PARSER.add_subparsers(
    dest="subcommand",
    required=True,
)

_DHASH_DEFAULT_STR = """
The "dhash" algorithm is used if none is given.
"""

_COMPARE_DESC = """
Compares a reference image to other images and returns a measure of visual similarity.
"""

_COMPARE_PARSER = _SUBCOMMAND_PARSER.add_parser(
    "compare",
    description=_COMPARE_DESC + " " + _DHASH_DEFAULT_STR,
    help=_COMPARE_DESC,
)

_COMPARE_PARSER.add_argument(
    "ref_path",
    type=Path,
    metavar="REF_PATH",
    default=None,
    help="""
    The reference image to compare among the search paths.
    """,
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
    """,
)

_add_algo_params_to_parser(_COMPARE_PARSER)
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
    """,
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
    """,
)

_DUPE_DESC = """
Finds images which hash to the same value within the given paths.
"""

_DUPE_PARSER = _SUBCOMMAND_PARSER.add_parser(
    "dupe",
    description=_DUPE_DESC + " " + _DHASH_DEFAULT_STR,
    help=_DUPE_DESC,
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
    """,
)

_add_algo_params_to_parser(_DUPE_PARSER)
_add_format_arg_to_parser(_DUPE_PARSER)

_DUPE_PARSER.set_defaults(command=DupeCommand.run)
