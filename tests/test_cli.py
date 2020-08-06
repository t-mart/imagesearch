"""Test the CLI."""
from unittest.mock import patch
from pathlib import Path

from imagesearch.config import Config
from imagesearch import Algorithm
from imagesearch.__main__ import main

def test_cli_hookup() -> None:
    """Tests whether the CLI's argument parsing hooks up correctly to the search method."""
    config = Config(
        ref_path=Path('needle.jpg'),
        search_paths=[Path('haystack/')],
        algorithm='colorhash',
        threshold=5,
        stop_on_first_match=True,
    )
    with patch('imagesearch.__main__.search') as mock_search_fn:
        main(config)
        mock_search_fn.assert_called_once_with(
            ref_path=Path('needle.jpg'),
            search_paths=[Path('haystack')],
            algorithm=Algorithm.COLORHASH,
            threshold=5,
            stop_on_first_match=True,
        )
