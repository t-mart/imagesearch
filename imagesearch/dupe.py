"""Functionality around finding duplicate images."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Set, Generator

from imagehash import ImageHash
import attr

from .fingerprint import Algorithm, ImageFingerprint


@attr.s(frozen=True, order=True, auto_attribs=True, kw_only=True)
class Dupe:
    """A set of image paths that hash to the same value with a given algorithm."""

    image_hash: ImageHash
    algorithm: Algorithm
    paths: Set[Path]

    @classmethod
    def find(
        cls, search_paths: Iterable[Path], algorithm: Algorithm
    ) -> Generator[Dupe, None, None]:
        """
        Yields Dupe objects for image files in the given search_paths.
        """
        hashes: Dict[ImageHash, Set[Path]] = defaultdict(set)

        for image_fingerprint in ImageFingerprint.recurse_paths(
            search_paths, algorithm
        ):
            hashes[image_fingerprint.image_hash].add(image_fingerprint.path)

        yield from [
            cls(image_hash=image_hash, algorithm=algorithm, paths=paths)
            for image_hash, paths in hashes.items()
            if len(paths) > 1
        ]
