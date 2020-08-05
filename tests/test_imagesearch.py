"""Tests for imagesearch."""
from pathlib import Path

import pytest

import imagesearch

TEST_IMAGE_DIR = Path('tests/images')
REF_IMAGE = TEST_IMAGE_DIR / 'en.wikipedia.org-Macaca_nigra_self-portrait_large.jpg'
UNSUPPORTED_IMAGE = TEST_IMAGE_DIR / 'not-an-image.txt'
TEST_IMAGE_SUBDIR_0 = TEST_IMAGE_DIR / 'subdir0'
TEST_IMAGE_SUBDIR_1_0 = TEST_IMAGE_DIR / 'subdir0/subdir1-0'
TEST_IMAGE_SUBDIR_1_1 = TEST_IMAGE_DIR / 'subdir0/subdir1-1'
NON_EXISTANT_FILE = TEST_IMAGE_DIR / 'does-not-exist'

def test_compares_all_files() -> None:
    """Tests that the directory is recursed"""
    results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[TEST_IMAGE_DIR],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=None
    ))
    assert len(results) == 10  # hardcoded. ugh.

def test_threshold() -> None:
    """Tests that all images return are <= threshold."""
    threshold = 10
    results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[TEST_IMAGE_DIR],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=threshold
    ))
    for result in results:
        assert result.diff <= threshold

def test_stop_on_first_match() -> None:
    """Tests that execution stops after 1 image under threshold."""
    no_threshold_results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[TEST_IMAGE_DIR],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=None
    ))
    biggest_diff = max(id.diff for id in no_threshold_results)

    with_threshold_results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[TEST_IMAGE_DIR],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=True,
        threshold=biggest_diff
    ))

    assert len(with_threshold_results) == 1

def test_multiple_search_dirs() -> None:
    """Tests multiple given search dirs"""
    results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[TEST_IMAGE_SUBDIR_1_0, TEST_IMAGE_SUBDIR_1_1],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=None
    ))
    assert len(results) == 5

def test_duplicate_search_dirs() -> None:
    """
    Tests that the number no image is checked twice if the 2 identical search directories are given.
    """
    results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[TEST_IMAGE_DIR, TEST_IMAGE_DIR],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=None
    ))
    assert len(results) == 10

def test_search_file() -> None:
    """Tests an explicit image path to search against."""
    results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[REF_IMAGE],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=None
    ))
    assert len(results) == 1

def test_search_dir_and_file() -> None:
    """Tests an explicit image path and another dir to search against."""
    results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[REF_IMAGE, TEST_IMAGE_SUBDIR_1_0],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=None
    ))
    assert len(results) == 4

def test_search_dir_and_file_within_dir() -> None:
    """
    Tests that, given a search dir and search file that's within that dir, the search file is only
    checked once.
    """
    results = list(imagesearch.search(
        ref_path=REF_IMAGE,
        search_paths=[REF_IMAGE, TEST_IMAGE_DIR],
        algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
        stop_on_first_match=False,
        threshold=None
    ))
    assert len(results) == 10

def test_unsupported_ref_image() -> None:
    """Tests that an unsupported ref image throws exception."""
    with pytest.raises(imagesearch.exceptions.UnsupportedImageException):
        list(imagesearch.search(
            ref_path=UNSUPPORTED_IMAGE,
            search_paths=[TEST_IMAGE_DIR],
            algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
            stop_on_first_match=False,
            threshold=None
        ))

def test_unsupported_explicit_search_file() -> None:
    """Tests that an unsupported explicit search file throws an exception."""
    with pytest.raises(imagesearch.exceptions.UnsupportedImageException):
        list(imagesearch.search(
            ref_path=REF_IMAGE,
            search_paths=[UNSUPPORTED_IMAGE],
            algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
            stop_on_first_match=False,
            threshold=None
        ))

def test_non_existant_ref_image() -> None:
    """Tests that a non-existant ref image throws an exception."""
    with pytest.raises(imagesearch.exceptions.DoesNotExistException):
        list(imagesearch.search(
            ref_path=NON_EXISTANT_FILE,
            search_paths=[TEST_IMAGE_DIR],
            algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
            stop_on_first_match=False,
            threshold=None
        ))

def test_non_existant_search_path() -> None:
    """Tests that a non-existant ref image throws an exception."""
    with pytest.raises(imagesearch.exceptions.NotSearchableException):
        list(imagesearch.search(
            ref_path=REF_IMAGE,
            search_paths=[NON_EXISTANT_FILE],
            algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
            stop_on_first_match=False,
            threshold=None
        ))

def test_invalid_threshold() -> None:
    """Tests that invalid thresholds throw an exception."""
    with pytest.raises(imagesearch.exceptions.ThresholdException):
        list(imagesearch.search(
            ref_path=REF_IMAGE,
            search_paths=[REF_IMAGE],
            algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
            stop_on_first_match=False,
            threshold=-1
        ))


def test_stop_on_first_match_without_threshold() -> None:
    """Tests that indicating to stop on first match without a threshold throws an exception."""
    with pytest.raises(imagesearch.exceptions.ThresholdException):
        list(imagesearch.search(
            ref_path=REF_IMAGE,
            search_paths=[REF_IMAGE],
            algorithm=imagesearch.Algorithm.PHASH_SIMPLE,
            stop_on_first_match=True,
            threshold=None
        ))
