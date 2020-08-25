"""Test the fingerprint module."""
import pytest

from imagesearch import Algorithm, ImageFingerprint
from imagesearch.exceptions import (
    UnsupportedImageException,
    NotReadableException,
)

from tests.fixtures import (
    REF_IMAGE,
    NON_EXISTANT_FILE,
    UNSUPPORTED_IMAGE,
    TEST_IMAGE_DIR,
    TEST_IMAGE_DIR_IMAGE_COUNT,
    TEST_IMAGE_SUBDIR_1_0,
    TEST_IMAGE_SUBDIR_1_0_IMAGE_COUNT,
    TEST_IMAGE_SUBDIR_1_1,
    TEST_IMAGE_SUBDIR_1_1_IMAGE_COUNT,
    IMAGE_IN_SUBDIR_1_1,
    IMAGE_NOT_IN_SUBDIR_1_1,
)


def test_image_fingerprint_from_path() -> None:
    """Tests that an ImageFingerprint can be created from a path."""
    algorithm = Algorithm.DHASH
    image_fingerprint = ImageFingerprint.from_path(path=REF_IMAGE, algorithm=algorithm,)

    assert image_fingerprint.path == REF_IMAGE
    assert image_fingerprint.algorithm == algorithm


def test_image_fingerprint_recurse_paths_single() -> None:
    """Test that recurse_paths on a file path yields a single ImageFingerprint."""
    image_fingerprints = list(
        ImageFingerprint.recurse_paths(
            search_paths=[REF_IMAGE], algorithm=Algorithm.DHASH,
        )
    )
    assert len(image_fingerprints) == 1


def test_image_fingerprint_recurse_paths_dir() -> None:
    """Test that recurse_paths on a dir path yields a number of ImageFingerprint objects."""
    image_fingerprints = list(
        ImageFingerprint.recurse_paths(
            search_paths=[TEST_IMAGE_DIR], algorithm=Algorithm.DHASH,
        )
    )
    assert len(image_fingerprints) == TEST_IMAGE_DIR_IMAGE_COUNT


def test_image_fingerprint_recurse_paths_dir_and_other_file() -> None:
    """
    Test that recurse_paths on a dir and other image path yields a the number of images in that dir
    plus 1.
    """
    paths = [TEST_IMAGE_SUBDIR_1_1, IMAGE_NOT_IN_SUBDIR_1_1]
    image_fingerprints = list(
        ImageFingerprint.recurse_paths(search_paths=paths, algorithm=Algorithm.DHASH,)
    )
    assert len(image_fingerprints) == 1 + TEST_IMAGE_SUBDIR_1_1_IMAGE_COUNT


def test_image_fingerprint_recurse_paths_dir_and_child_file() -> None:
    """
    Test that recurse_paths on a dir and another image that's a child of that dir yields a the
    number of images in that dir. In other words, the child image doesn't get fingerprinted twice.
    """
    paths = [TEST_IMAGE_SUBDIR_1_1, IMAGE_IN_SUBDIR_1_1]
    image_fingerprints = list(
        ImageFingerprint.recurse_paths(search_paths=paths, algorithm=Algorithm.DHASH,)
    )
    assert len(image_fingerprints) == TEST_IMAGE_SUBDIR_1_1_IMAGE_COUNT


def test_image_fingerprint_recurse_paths_same_dir_twice() -> None:
    """
    Test that recurse_paths on a dir and the same dir just yields fingerprints that are deduped.
    """
    paths = [TEST_IMAGE_SUBDIR_1_1, TEST_IMAGE_SUBDIR_1_1]
    image_fingerprints = list(
        ImageFingerprint.recurse_paths(search_paths=paths, algorithm=Algorithm.DHASH,)
    )
    assert len(image_fingerprints) == TEST_IMAGE_SUBDIR_1_1_IMAGE_COUNT


def test_image_fingerprint_recurse_paths_two_dirs() -> None:
    """
    Test that recurse_paths on a dir and the another dir just yields fingerprints for each image
    in both dirs.
    """
    paths = [TEST_IMAGE_SUBDIR_1_1, TEST_IMAGE_SUBDIR_1_0]
    image_fingerprints = list(
        ImageFingerprint.recurse_paths(search_paths=paths, algorithm=Algorithm.DHASH)
    )
    assert (
        len(image_fingerprints)
        == TEST_IMAGE_SUBDIR_1_1_IMAGE_COUNT + TEST_IMAGE_SUBDIR_1_0_IMAGE_COUNT
    )


def test_image_fingerprint_recurse_paths_two_files() -> None:
    """
    Test that recurse_paths on a dir and the another dir just yields fingerprints for each image
    in both dirs.
    """
    paths = [IMAGE_IN_SUBDIR_1_1, IMAGE_NOT_IN_SUBDIR_1_1]
    image_fingerprints = list(
        ImageFingerprint.recurse_paths(search_paths=paths, algorithm=Algorithm.DHASH,)
    )
    assert len(image_fingerprints) == 2


def test_image_fingerprint_recurse_paths_non_existant() -> None:
    """Tests that a non-existant image throws an exception."""
    paths = [NON_EXISTANT_FILE]
    with pytest.raises(NotReadableException):
        list(
            ImageFingerprint.recurse_paths(
                search_paths=paths, algorithm=Algorithm.DHASH
            )
        )


def test_image_fingerprint_recurse_paths_unsupported() -> None:
    """Tests that a non-existant image throws an exception."""
    paths = [UNSUPPORTED_IMAGE]
    with pytest.raises(UnsupportedImageException):
        list(
            ImageFingerprint.recurse_paths(
                search_paths=paths, algorithm=Algorithm.DHASH
            )
        )


def test_image_fingerprint_recurse_paths_skips_non_image_files_in_dir() -> None:
    """Test that non-image files in directories are skipped."""
    image_fingerprints = ImageFingerprint.recurse_paths(
        search_paths=[TEST_IMAGE_DIR], algorithm=Algorithm.DHASH
    )
    assert not any(
        fingerprint.path == UNSUPPORTED_IMAGE for fingerprint in image_fingerprints
    )
