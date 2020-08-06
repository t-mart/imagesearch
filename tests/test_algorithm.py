"""Test the algorithm module."""
from pytest import raises

from imagesearch import Algorithm
from imagesearch.exceptions import UnknownAlgorithmException

def test_valid_from_name() -> None:
    """Tests whether lookup of a valid name is successful."""
    assert Algorithm.from_name('ahash') == Algorithm.AHASH

def test_invalid_from_name() -> None:
    """Tests whether lookup of a valid name is successful."""
    with raises(UnknownAlgorithmException):
        Algorithm.from_name('not valid')

def test_algo_names() -> None:
    """Tests whether the algo_names() method returns a list of algorithm names."""
    names = Algorithm.algo_names()
    assert len(names) > 0
    assert all(isinstance(item, str) for item in names)
