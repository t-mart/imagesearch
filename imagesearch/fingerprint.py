"""Compute visual fingerprints of images."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List
from enum import Enum, unique

import imagehash
from PIL import Image, UnidentifiedImageError

from .exceptions import (
    UnsupportedImageException,
    DoesNotExistException,
    FileNotReadableException,
    UnknownAlgorithmException,
)


@unique
class Algorithm(Enum):
    """
    An enumeration of the algorithms provided by imagehash, along with a name and description.
    """
    AHASH = (
        'ahash',
        imagehash.average_hash,
        'Average hashing'
    )
    PHASH = (
        'phash',
        imagehash.phash,
        '2-axis perceptual hashing'
    )
    PHASH_SIMPLE = (
        'phash-simple',
        imagehash.phash_simple,
        '1-axis perceptual hashing'
    )
    DHASH = (
        'dhash',
        imagehash.dhash,
        'Horizontal difference hashing'
    )
    DHASH_VERT = (
        'dhash-vert',
        imagehash.dhash_vertical,
        'Vertical difference hashing'
    )
    WHASH_HAAR = (
        'whash-haar',
        imagehash.whash,
        'Haar wavelet hashing'
    )
    WHASH_DB4 = (
        'whash-db4',
        lambda img: imagehash.whash(img, mode='db4'),
        'Daubechies wavelet hashing'
    )
    COLORHASH = (
        'colorhash',
        imagehash.colorhash,
        'HSV color hashing'
    )

    @classmethod
    def from_name(cls, name: str) -> Algorithm:
        """Returns an algorithm by name."""
        name_map: Dict[str, Algorithm] = {
            algo.algo_name: algo for algo in list(Algorithm)
        }
        if name not in name_map:
            raise UnknownAlgorithmException(f"No algorithm with name {name}")
        return name_map[name]

    @classmethod
    def algo_names(cls) -> List[str]:
        """Return a list of all the algorithm names."""
        return [algo.algo_name for algo in list(Algorithm)]

    def __init__(
            self,
            algo_name: str,
            method: Callable[[Image], imagehash.ImageHash],
            description: str,
    ):
        self.algo_name = algo_name
        self.method = method
        self.description = description

    def hash_path(self, path: Path) -> imagehash.ImageHash:
        """Compute the visual fingerprint of image at path with an algorithm."""
        try:
            image = Image.open(path)
        except UnidentifiedImageError as exc:
            raise UnsupportedImageException(
                f"Path {path} is not a supported image format: {exc}")
        except FileNotFoundError as exc:
            raise DoesNotExistException(
                f"Path {path} could not be found: {exc}")
        except PermissionError as exc:
            raise FileNotReadableException(
                f"Could not open path {path} for reading: {exc}")
        return self.method(image)
