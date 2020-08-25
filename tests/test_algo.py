"""Test the algorithm module."""
from unittest.mock import patch, MagicMock
import platform

import pytest

from imagesearch import Algorithm
from imagesearch.exceptions import (
    UnknownAlgorithmException,
    UnsupportedImageException,
    DoesNotExistException,
    NotReadableException,
)

from tests.fixtures import (
    REF_IMAGE,
    NON_EXISTANT_FILE,
    UNSUPPORTED_IMAGE,
    TEST_IMAGE_DIR,
)


def test_algorithm_valid_from_name() -> None:
    """Tests whether lookup of a valid name is successful."""
    assert Algorithm.from_name("ahash") == Algorithm.AHASH


def test_algorithm_invalid_from_name() -> None:
    """Tests whether lookup of a valid name is successful."""
    with pytest.raises(UnknownAlgorithmException):
        Algorithm.from_name("bogus")


def test_algorithm_hash_path_unsupported() -> None:
    """Tests that trying to hash a path that's not an image throws an exception."""
    with pytest.raises(UnsupportedImageException):
        Algorithm.DHASH(UNSUPPORTED_IMAGE)


def test_algorithm_hash_path_non_existant() -> None:
    """Tests that trying to hash a path that does not exist throws an exception."""
    with pytest.raises(DoesNotExistException):
        Algorithm.DHASH(NON_EXISTANT_FILE)


def test_algorithm_hash_path_restrictive_permissions() -> None:
    """Tests that trying to hash a path that's not readable throws an exception."""
    # TODO: is there a way to create an real file without read perms that can still be checked in?
    # Or maybe use a virtual FS?
    with pytest.raises(NotReadableException):
        with patch("PIL.Image.open") as mock_image_open:
            mock_image_open.side_effect = PermissionError()
            Algorithm.DHASH(REF_IMAGE)


def test_algorithm_hash_path_dir() -> None:
    """Tests that trying to hash a dir path throws an exception."""
    if platform.system() == "Windows":
        # On windows, Image.open() on a directory raises a PermissionError, so patch in a
        # IsADirectoryError to cover that case when testing on Windows too.
        with pytest.raises(NotReadableException):
            with patch("PIL.Image.open") as mock_image_open:
                mock_image_open.side_effect = IsADirectoryError()
                Algorithm.DHASH(REF_IMAGE)
    else:
        # On linux (and probably everything else?), it raises a IsADirectoryError, so we can test
        # without patching (in other words, this is the native behavior.)
        with pytest.raises(NotReadableException):
            Algorithm.DHASH(TEST_IMAGE_DIR)
