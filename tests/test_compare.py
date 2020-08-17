"""Tests for ImageDiff.compare()."""
import pytest

from imagesearch import ImageDiff, Algorithm
from imagesearch.exceptions import (
    UnsupportedImageException,
    ThresholdException,
    DoesNotExistException,
)

from .fixtures import (
    REF_IMAGE,
    TEST_IMAGE_DIR,
    UNSUPPORTED_IMAGE,
    NON_EXISTANT_FILE,
)


def test_threshold() -> None:
    """Tests that all images return are <= threshold."""
    threshold = 30
    results = list(
        ImageDiff.compare(
            ref_path=REF_IMAGE,
            search_paths=[TEST_IMAGE_DIR],
            algorithm=Algorithm.DHASH,
            stop_on_first_match=False,
            threshold=threshold,
        )
    )
    for result in results:
        assert result.diff <= threshold


def test_stop_on_first_match() -> None:
    """Tests that execution stops after 1 image under threshold."""
    no_threshold_results = list(
        ImageDiff.compare(
            ref_path=REF_IMAGE,
            search_paths=[TEST_IMAGE_DIR],
            algorithm=Algorithm.DHASH,
            stop_on_first_match=False,
            threshold=None,
        )
    )
    biggest_diff = max(id.diff for id in no_threshold_results)

    with_threshold_results = list(
        ImageDiff.compare(
            ref_path=REF_IMAGE,
            search_paths=[TEST_IMAGE_DIR],
            algorithm=Algorithm.DHASH,
            stop_on_first_match=True,
            threshold=biggest_diff,
        )
    )

    assert len(with_threshold_results) == 1


def test_unsupported_ref_image() -> None:
    """Tests that an unsupported ref image throws exception."""
    with pytest.raises(DoesNotExistException):
        list(
            ImageDiff.compare(
                ref_path=NON_EXISTANT_FILE,
                search_paths=[TEST_IMAGE_DIR],
                algorithm=Algorithm.DHASH,
                stop_on_first_match=False,
                threshold=None,
            )
        )


def test_non_existant_ref_image() -> None:
    """Tests that an unsupported ref image throws exception."""
    with pytest.raises(UnsupportedImageException):
        list(
            ImageDiff.compare(
                ref_path=UNSUPPORTED_IMAGE,
                search_paths=[TEST_IMAGE_DIR],
                algorithm=Algorithm.DHASH,
                stop_on_first_match=False,
                threshold=None,
            )
        )


def test_invalid_threshold() -> None:
    """Tests that invalid thresholds throw an exception."""
    with pytest.raises(ThresholdException):
        list(
            ImageDiff.compare(
                ref_path=REF_IMAGE,
                search_paths=[REF_IMAGE],
                algorithm=Algorithm.DHASH,
                stop_on_first_match=False,
                threshold=-1,
            )
        )


def test_stop_on_first_match_without_threshold() -> None:
    """Tests that indicating to stop on first match without a threshold throws an exception."""
    with pytest.raises(ThresholdException):
        list(
            ImageDiff.compare(
                ref_path=REF_IMAGE,
                search_paths=[REF_IMAGE],
                algorithm=Algorithm.DHASH,
                stop_on_first_match=True,
                threshold=None,
            )
        )
