"""Functionality around searching paths and determining visual differences."""
from __future__ import annotations

from pathlib import Path
from typing import Generator, List, Optional, Set

import attr

from .exceptions import (
    ThresholdException,
    DoesNotExistException,
    NotSearchableException,
    UnsupportedImageException,
    FileNotReadableException
)
from .fingerprint import Algorithm


@attr.s(frozen=True, auto_attribs=True, kw_only=True, order=True)
class ImageDiff:
    """The difference in hash between this image and a reference image."""
    path: Path = attr.ib(order=False)
    diff: int

    def output_line(self) -> str:
        """Return the output string of this object"""
        return f"{self.diff}\t{self.path}"


@attr.s(frozen=True, auto_attribs=True, kw_only=True, order=False)
class SearchPathFile:
    """
    A file that should be searched.

    path: The Path to the file
    explicit: Whether the file was explicitly asked to be compared (i.e. was provided as a search
        path and not a directory's child). If so, and the file is not a valid image, the we can
        error.
    """
    path: Path
    explicit: bool

    def fs_valid(self) -> bool:
        """
        Returns if the file is valid from an filesystem perspective: it's a file (not a directory,
        etc.)
        """
        return self.path.is_file()


def iterate_paths(search_path: Path) -> Generator[SearchPathFile, None, None]:
    """
    Yield all existing subpaths from a given path.

    This means that if the path is a:
        - file, then yield that file if it is an allowed extension
        - directory, then yield all files under that directory that are allowed extensions
    """
    if search_path.is_file():
        yield SearchPathFile(
            path=search_path,
            explicit=True
        )

    elif search_path.is_dir():
        for child_path in search_path.rglob("*"):
            if child_path.is_file():
                yield SearchPathFile(
                    path=child_path,
                    explicit=False
                )

    else:
        raise NotSearchableException(
            f'Search path "{search_path}" is not a file or directory.'
        )


def check_threshold(threshold: Optional[int]) -> None:
    """Checks the threshold for nonnegativity."""
    if threshold is not None and threshold < 0:
        raise ThresholdException("Threshold must be nonnegative.")


def check_stop_on_first_match(stop_on_first_match: bool, threshold: Optional[int]) -> None:
    """
    Checks that we can stop on the first match, which is only possible if a threshold is specified.
    """
    if threshold is None and stop_on_first_match:
        raise ThresholdException(
            "If stopping on first match, a threshold must be specified."
        )


def search(
        ref_path: Path,
        search_paths: List[Path],
        algorithm: Algorithm,
        stop_on_first_match: bool = False,
        threshold: Optional[int] = None,
) -> Generator[ImageDiff, None, None]:
    """
    Returns a generator of ImageDiff objects for all images in search paths against the ref path
    image.
    """
    check_threshold(threshold)
    check_stop_on_first_match(stop_on_first_match, threshold)

    reference_image_hash = algorithm.hash_path(ref_path)

    seen_images: Set[Path] = set()

    for search_path in search_paths:
        for child_path in iterate_paths(search_path):

            if child_path.path in seen_images and not child_path.explicit:
                continue
            seen_images.add(child_path.path)

            try:
                image_hash = algorithm.hash_path(child_path.path)
            except (
                    UnsupportedImageException,
                    DoesNotExistException,
                    FileNotReadableException
            ):
                if child_path.explicit:
                    raise
                continue

            diff = image_hash - reference_image_hash
            if threshold is None or diff <= threshold:
                yield ImageDiff(
                    path=child_path.path,
                    diff=diff
                )
                if stop_on_first_match:
                    break
