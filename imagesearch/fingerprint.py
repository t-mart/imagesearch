"""Compute visual fingerprints of images."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Generator, Iterable, Set
from enum import Enum, unique

import imagehash
from PIL import Image, UnidentifiedImageError
import attr

from .exceptions import (
    UnsupportedImageException,
    DoesNotExistException,
    NotReadableException,
    UnknownAlgorithmException,
    HashingException,
)


@unique
class Algorithm(Enum):
    """
    An enumeration of the algorithms provided by imagehash, along with a name and description.
    """

    AHASH = (
        "ahash",
        imagehash.average_hash,
        "Average hashing",
    )
    PHASH = (
        "phash",
        imagehash.phash,
        "2-axis perceptual hashing",
    )
    PHASH_SIMPLE = (
        "phash-simple",
        imagehash.phash_simple,
        "1-axis perceptual hashing",
    )
    DHASH = (
        "dhash",
        imagehash.dhash,
        "Horizontal difference hashing",
    )
    DHASH_VERT = (
        "dhash-vert",
        imagehash.dhash_vertical,
        "Vertical difference hashing",
    )
    WHASH_HAAR = (
        "whash-haar",
        imagehash.whash,
        "Haar wavelet hashing",
    )
    WHASH_DB4 = (
        "whash-db4",
        lambda img: imagehash.whash(img, mode="db4"),
        "Daubechies wavelet hashing",
    )
    COLORHASH = (
        "colorhash",
        imagehash.colorhash,
        "HSV color hashing",
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

    @classmethod
    def supported_names(cls) -> str:
        """Returns a comma-separated string of all the algo names."""
        return ", ".join(algo.algo_name.lower() for algo in list(Algorithm))

    @classmethod
    def all_descriptions(cls) -> str:
        """Returns a comma-separated list of algorithm names and what they do."""
        return ", ".join(
            f"{algo.algo_name} = {algo.description}" for algo in list(Algorithm)
        )

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
        """
        Compute the visual fingerprint of image at path with an algorithm.

        Pillow accepts many, many image formats. Instead of trying to analyze what's acceptable
        early, we just attempt to open the path with it and handle exceptions appropriately.
        """
        try:
            image = Image.open(path)
        except UnidentifiedImageError as exc:
            raise UnsupportedImageException(
                f"Path {path} is not a supported image format: {exc}"
            )
        except FileNotFoundError as exc:
            raise DoesNotExistException(f"Path {path} could not be found: {exc}")
        except PermissionError as exc:
            raise NotReadableException(f"Could not open path {path} for reading: {exc}")
        except IsADirectoryError as exc:
            raise NotReadableException(f"Path {path} is a directory: {exc}")
        return self.method(image)


@attr.s(frozen=True, auto_attribs=True, kw_only=True, order=False)
class ImageFingerprint:
    """
    A file that will be fingerprinted.

    path: The Path to the file
    explicit: Whether the file was explicitly asked to be fingerprinted (i.e. was provided as a
        search path and not a directory's child).
    """

    path: Path
    image_hash: imagehash.ImageHash
    algorithm: Algorithm

    @classmethod
    def from_path(cls, path: Path, algorithm: Algorithm) -> ImageFingerprint:
        """Create an ImageFingerprint from just a path (the hashing happens here)."""
        image_hash = algorithm.hash_path(path)

        return cls(path=path, image_hash=image_hash, algorithm=algorithm,)

    @classmethod
    def recurse_paths(
        cls, search_paths: Iterable[Path], algorithm: Algorithm,
    ) -> Generator[ImageFingerprint, None, None]:
        """
        Yields ImageFingerprint objects for all child paths in the iterable search_paths that are
        images.

        search_paths should be a list of Path objects. They may point to different types of path:
            - If the path is actually a directory, it will be recursed into and only hashable images
              yielded. This avoids any issues with hidden files, files that aren't images, etc.
            - If the path is a file, and it is not hashable, an exception will be thrown. Otherwise,
              it is yielded.

        Only unique paths will be yielded.
        """
        seen_paths: Set[Path] = set()

        for search_path in search_paths:

            if search_path.is_file():
                if search_path in seen_paths:
                    continue

                # this may throw a HashingException. we let it bubble up because the file was
                # explicitly named.
                yield ImageFingerprint.from_path(
                    path=search_path, algorithm=algorithm,
                )

                seen_paths.add(search_path)

            elif search_path.is_dir():
                for child_path in search_path.rglob("*"):
                    if child_path.is_file() and child_path not in seen_paths:
                        try:
                            yield ImageFingerprint.from_path(
                                path=child_path, algorithm=algorithm
                            )
                        except HashingException:
                            # here, we don't care about HashingExceptions because we're just
                            # scanning every child file. we don't require everything to be an image
                            # in a given dir. This is for usability (don't need to cleanse a dir to
                            # only contain images) and to workaround unavoidable hidden files
                            # (Thumbs.db, .DS_Store, etc)
                            continue
                        finally:
                            seen_paths.add(child_path)

            else:
                raise NotReadableException(
                    f'Search path "{search_path}" is not a file or directory that can be read.'
                )
