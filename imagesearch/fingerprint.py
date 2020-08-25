"""Compute visual fingerprints of on image files and directories."""
from __future__ import annotations

from pathlib import Path
from typing import Generator, Iterable, Set, List, Optional, Dict, Union

import imagehash
import attr

from imagesearch.progress import SearchProgressBar
from imagesearch.algo import Algorithm
from imagesearch.exceptions import (
    NotReadableException,
    HashingException,
)


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
    def from_path(
        cls,
        path: Path,
        algorithm: Algorithm,
        algo_params: Optional[Dict[str, Optional[Union[str, bool, int]]]] = None
    ) -> ImageFingerprint:
        """Create an ImageFingerprint from just a path (the hashing happens here)."""
        image_hash = algorithm(
            path=path,
            algo_params=algo_params
        )

        return cls(path=path, image_hash=image_hash, algorithm=algorithm)

    @attr.s(frozen=True, auto_attribs=True, kw_only=True, order=False)
    class _WalkedPath:
        path: Path
        from_dir_search: bool

    @classmethod
    def _walk_paths(
        cls,
        search_paths: Iterable[Path],
        pbar: Optional[SearchProgressBar] = None,
    ) -> List[_WalkedPath]:
        """
        Walk all paths in search_paths.

        We return a list so the progress bar can know the length. Unfortunately, this puts all paths
        in memory.
        """
        def add_to_pbar() -> None:
            if pbar is not None:
                pbar.add_to_total()

        paths: List[ImageFingerprint._WalkedPath] = []

        for search_path in search_paths:

            if search_path.is_file():
                paths.append(ImageFingerprint._WalkedPath(
                    path=search_path,
                    from_dir_search=False
                ))
                add_to_pbar()

            elif search_path.is_dir():
                for child_path in search_path.rglob("*"):
                    if child_path.is_file():
                        paths.append(ImageFingerprint._WalkedPath(
                            path=child_path,
                            from_dir_search=True
                        ))
                        add_to_pbar()

            else:
                raise NotReadableException(
                    f'Search path "{search_path}" is not a file or directory that can be read.'
                )

        return paths

    @classmethod
    def recurse_paths(
        cls,
        search_paths: Iterable[Path],
        algorithm: Algorithm,
        algo_params: Optional[Dict[str, Optional[Union[str, bool, int]]]] = None,
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
        pbar = SearchProgressBar()

        with pbar:
            paths = cls._walk_paths(search_paths, pbar=pbar)

            for walked_path in paths:
                if walked_path.path in seen_paths:
                    pbar.add_skip(walked_path.path)
                    continue

                try:
                    yield ImageFingerprint.from_path(
                        path=walked_path.path,
                        algorithm=algorithm,
                        algo_params=algo_params,
                    )
                except HashingException:
                    if walked_path.from_dir_search:
                        pbar.add_skip(walked_path.path)
                        continue
                    raise
                else:
                    pbar.add_hash(walked_path.path)
                finally:
                    seen_paths.add(walked_path.path)
