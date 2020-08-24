"""Functionality around searching paths and determining visual differences."""
from __future__ import annotations

from pathlib import Path
from typing import Generator, List, Optional

import attr

from imagesearch.exceptions import ThresholdException
from imagesearch.fingerprint import Algorithm, ImageFingerprint


@attr.s(frozen=True, auto_attribs=True, kw_only=True, order=True)
class ImageDiff:
    """The difference in hash between this image and a reference image."""

    path: Path = attr.ib(order=False)
    diff: int

    @staticmethod
    def _check_threshold(threshold: Optional[int]) -> None:
        """Checks the threshold for nonnegativity."""
        if threshold is not None and threshold < 0:
            raise ThresholdException("Threshold must be nonnegative.")

    @staticmethod
    def _check_stop_on_first_match(
        stop_on_first_match: bool, threshold: Optional[int]
    ) -> None:
        """
        Checks that we can stop on the first match, which is only possible if a threshold is
        specified.
        """
        if threshold is None and stop_on_first_match:
            raise ThresholdException(
                "If stopping on first match, a threshold must be specified."
            )

    @classmethod
    def compare(
        cls,
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
        cls._check_threshold(threshold)
        cls._check_stop_on_first_match(stop_on_first_match, threshold)

        reference_fingerprint = ImageFingerprint.from_path(ref_path, algorithm)

        for image_fingerprint in ImageFingerprint.recurse_paths(
            search_paths, algorithm
        ):
            diff = image_fingerprint.image_hash - reference_fingerprint.image_hash
            if threshold is None or diff <= threshold:
                yield ImageDiff(path=image_fingerprint.path, diff=diff)
                if stop_on_first_match:
                    break
