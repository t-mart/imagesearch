"""Algorithms for fingerprinting"""
from __future__ import annotations
from pathlib import Path
from typing import Callable, Mapping, Dict, List, Optional, Iterator, Union, Any
from enum import Enum, unique
import warnings
from contextlib import contextmanager

import imagehash
from PIL import Image, UnidentifiedImageError
import attr

from imagesearch.exceptions import (
    UnsupportedImageException,
    DoesNotExistException,
    NotReadableException,
    UnknownAlgorithmException,
)


@attr.s(frozen=True, auto_attribs=True, order=False, kw_only=True)
class AlgorithmParameter:
    """An argument to an imagehash algorithm call."""
    name: str
    default_value: Optional[Union[bool, str, int]]
    converter: Callable[[Any], Any]
    help: str


@unique
class Algorithm(Enum):
    """
    An enumeration of the algorithms provided by imagehash, along with a name and description.
    """

    AHASH = (
        "ahash",
        imagehash.average_hash,
        "Average hashing.",
        [
            AlgorithmParameter(
                name="hash_size",
                default_value=8,
                converter=int,
                help="The number of bytes in the hash."
            ),
        ],
    )

    PHASH = (
        "phash",
        imagehash.phash,
        "2-axis perceptual hashing.",
        [
            AlgorithmParameter(
                name="hash_size",
                default_value=8,
                converter=int,
                help="The number of bytes in the hash."
            ),
            AlgorithmParameter(
                name="highfreq_factor",
                default_value=4,
                converter=int,
                help="High frequency factor."
            ),
        ],
    )

    PHASH_SIMPLE = (
        "phash-simple",
        imagehash.phash_simple,
        "1-axis perceptual hashing.",
        [
            AlgorithmParameter(
                name="hash_size",
                default_value=8,
                converter=int,
                help="The number of bytes in the hash."
            ),
            AlgorithmParameter(
                name="highfreq_factor",
                default_value=4,
                converter=int,
                help="High frequency factor."
            ),
        ],
    )

    DHASH = (
        "dhash",
        imagehash.dhash,
        "Horizontal difference hashing.",
        [
            AlgorithmParameter(
                name="hash_size",
                default_value=8,
                converter=int,
                help="The number of bytes in the hash."
            ),
        ],
    )

    DHASH_VERT = (
        "dhash-vert",
        imagehash.dhash_vertical,
        "Vertical difference hashing.",
        [
            AlgorithmParameter(
                name="hash_size",
                default_value=8,
                converter=int,
                help="The number of bytes in the hash."
            ),
        ],
    )

    WHASH = (
        "whash",
        imagehash.whash,
        "Wavelet hashing.",
        [
            AlgorithmParameter(
                name="hash_size",
                default_value=8,
                converter=int,
                help="The number of bytes in the hash."
            ),
            # We could write a more custom converter for image_scale, but it's already tightly-
            # coupled to our custom algorithm argument parsing. In the meantime, we have the
            # limitation mentioned in the help text below.
            AlgorithmParameter(
                name="image_scale",
                default_value=None,
                converter=int,
                help="""
                Must be power of 2 and less than image size. If None (the default), image_scale is
                set to max power of 2 for an input image. It's currently not possible to explicitly
                set the value to None, so just omit it.
                """.strip()
            ),
            AlgorithmParameter(
                name="mode",
                default_value="haar",
                converter=str,
                help="The mode. Currently \"haar\" and \"db4\" are supported."
            ),
            AlgorithmParameter(
                name="remove_max_haar_ll",
                default_value=True,
                converter=bool,
                help="""
                Remove the lowest low level (LL) frequency using Haar wavelet. TO SET TO FALSE, set
                to a blank value, such as "remove_max_haar=".
                """.strip()
            ),
        ],
    )

    COLORHASH = (
        "colorhash",
        imagehash.colorhash,
        "HSV color hashing.",
        [
            AlgorithmParameter(
                name="binbits",
                default_value=3,
                converter=int,
                help="The number of bits to use to encode each pixel fractions."
            ),
        ],
    )

    @classmethod
    def from_name(cls, name: str) -> Algorithm:
        """Returns an algorithm by name."""
        name_map: Dict[str, Algorithm] = {
            algo.algo_name: algo for algo in list(Algorithm)
        }
        name_normalized = name.lower()
        if name_normalized not in name_map:
            raise UnknownAlgorithmException(f"No algorithm with name {name}")
        return name_map[name_normalized]

    def __init__(
        self,
        algo_name: str,
        method: Callable[..., imagehash.ImageHash],
        description: str,
        params: List[AlgorithmParameter]
    ):
        self.algo_name = algo_name
        self.method = method
        self.description = description
        self.params = params

    def __call__(
        self,
        path: Path,
        algo_params: Optional[Mapping[str, Optional[Union[str, bool, int]]]] = None
    ) -> imagehash.ImageHash:
        """
        Compute the visual fingerprint of image at path with an algorithm.

        Pillow accepts many, many image formats. Instead of trying to analyze what's acceptable
        early, we just attempt to open the path with it and handle exceptions appropriately.
        """

        @contextmanager
        def ignore_pil_warnings() -> Iterator[None]:
            """
            Ignores PIL warnings that sometimes popup. Have seen them for too-big of files on open()
            and for transparency layers when reading.
            """
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", module=r"PIL\.Image")
                yield

        if algo_params is None:
            algo_params = {}

        try:
            with ignore_pil_warnings():
                image = Image.open(path)
        except UnidentifiedImageError as exc:
            raise UnsupportedImageException(
                f"Path {path} is not a supported image format: {exc}"
            )
        except FileNotFoundError as exc:
            raise DoesNotExistException(
                f"Path {path} could not be found: {exc}")
        except PermissionError as exc:
            raise NotReadableException(
                f"Could not open path {path} for reading: {exc}")
        except IsADirectoryError as exc:
            raise NotReadableException(f"Path {path} is a directory: {exc}")

        with ignore_pil_warnings():
            # TODO, providing algo_params increases the surface area of exceptions we can expect. how
            # should we handle these?
            return self.method(image=image, **algo_params)
