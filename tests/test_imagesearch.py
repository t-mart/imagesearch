"""Test general qualities of the module."""
from imagesearch import __version__

def test_version() -> None:
    """Tests the version of the application"""
    assert __version__ == '0.1.2'
