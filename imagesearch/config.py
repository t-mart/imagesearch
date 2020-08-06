"""Functionality related to configuration."""

from __future__ import annotations
import argparse
from typing import Type, List, Optional
from pathlib import Path

import attr

from .fingerprint import Algorithm
from . import __version__


@attr.s(frozen=True, auto_attribs=True, order=False, kw_only=True)
class Config:
    """Holds configuration parameters."""

    ref_path: Path
    search_paths: List[Path]
    algorithm: str
    stop_on_first_match: bool
    threshold: Optional[int]

    @classmethod
    def from_args(cls: Type[Config], args: Optional[List[str]] = None) -> Config:
        """Generate a _Config from command line arguments."""
        parser = argparse.ArgumentParser(
            prog="imagesearch",
            description=(
                "Returns the similiarity between a reference image and a set of other images."
            ),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        parser.add_argument(
            '--version',
            action='version',
            version=__version__
        )

        parser.add_argument(
            'ref_path',
            type=Path,
            help="The reference image to compare among the search paths."
        )

        parser.add_argument(
            'search_path',
            nargs='+',
            type=Path,
            help=(
                "The path(s) of other images to compare against the reference image. This argument "
                "may be supplied multiples times. The path may be either a file (for explicit "
                "comparison) or a directory that will be recursively searched for image files."
            )
        )

        each_algo_help_str = ", ".join(
            f"{algo.algo_name} = {algo.description}" for algo in list(Algorithm)
        )
        parser.add_argument(
            "-a",
            "--algorithm",
            action="store",
            default='ahash',
            choices=Algorithm.algo_names(),
            help=(
                "The algorithm to use to fingerprint the images. See the imagehash library for "
                f"documentation on how each works. {each_algo_help_str}."
            ),
        )

        parser.add_argument(
            '-1',
            '--stop-on-first-match',
            action='store_true',
            help=(
                'Stop searching immediately after the first image with diff <= threshold is found '
                '(instead of continuing to search through all search paths), which also means that '
                'this argument must be used with the threshold argument as well . If multiple '
                'matches do exist, the result is arbitrary. This argument is intended to search '
                'through a large set of images where only a single image is desired.'
            )
        )

        parser.add_argument(
            '-t',
            '--threshold',
            type=int,
            default=None,
            help=(
                'The the maximum difference at which to consider 2 images as a match. Lower '
                'numbers mean closer match. This value is subjective and depends on the hash '
                'algorithm used, so testing without a threshold may be useful to feel for the '
                'values. Omit to use an infinite threshold.'
            )
        )

        parsed_args = parser.parse_args(args=args)

        return cls(
            ref_path=parsed_args.ref_path,
            search_paths=parsed_args.search_path,
            algorithm=parsed_args.algorithm,
            stop_on_first_match=parsed_args.stop_on_first_match,
            threshold=parsed_args.threshold,
        )

def get_config(args: Optional[List[str]] = None) -> Config:
    """Returns the configuration"""
    return Config.from_args(args)
