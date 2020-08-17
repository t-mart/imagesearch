"""Tests for imagesearch."""
import pytest

from imagesearch import Dupe, Algorithm
from imagesearch.exceptions import (
    UnsupportedImageException,
    NotReadableException,
)

from .fixtures import (
    TEST_IMAGE_DIR,
    DUPE_PATH_A,
    DUPE_PATH_B,
    NON_DUPE_PATH,
    UNSUPPORTED_IMAGE,
    NON_EXISTANT_FILE,
)


def test_dupe_found() -> None:
    """Tests that a dupe is found."""
    dupes = list(Dupe.find(search_paths=[TEST_IMAGE_DIR], algorithm=Algorithm.DHASH,))

    assert len(dupes) == 1

    dupe = dupes[0]
    assert dupe.paths == set([DUPE_PATH_A, DUPE_PATH_B])


def test_no_dupe_for_single_path() -> None:
    """Tests that no duplicate image is found when 1 file is in search_paths."""
    dupes = list(Dupe.find(search_paths=[DUPE_PATH_A], algorithm=Algorithm.DHASH,))

    assert len(dupes) == 0


def test_no_dupe_for_different_images() -> None:
    """Tests that no dupes are produced for actually different images."""
    dupes = list(
        Dupe.find(search_paths=[DUPE_PATH_A, NON_DUPE_PATH], algorithm=Algorithm.DHASH,)
    )

    assert len(dupes) == 0


def test_unsupported_image() -> None:
    """Tests that an unsupported image in search_paths throws exception."""
    with pytest.raises(UnsupportedImageException):
        list(
            Dupe.find(
                search_paths=[UNSUPPORTED_IMAGE, DUPE_PATH_A],
                algorithm=Algorithm.DHASH,
            )
        )


def test_non_existant_image() -> None:
    """Tests that a non-existant image in search_paths throws an exception."""
    with pytest.raises(NotReadableException):
        list(
            Dupe.find(
                search_paths=[NON_EXISTANT_FILE, DUPE_PATH_A],
                algorithm=Algorithm.DHASH,
            )
        )
