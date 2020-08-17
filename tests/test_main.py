"""Tests the entry point module"""
from unittest.mock import patch

from imagesearch.__main__ import main
from imagesearch.status import ExitStatus

from .image_helpers import NON_EXISTANT_FILE, REF_IMAGE


def test_okay_exit() -> None:
    """Test successful operation exits with the right exit code."""
    with patch("sys.exit") as mock_exit:
        main(["imagesearch", "dupe", str(REF_IMAGE)])

        mock_exit.assert_called_once_with(ExitStatus.SUCCESS)


def test_keyboard_interrupt_exit(capsys) -> None:  # type: ignore
    """Test that a keyboard interrupt exits with the right exit code."""
    with patch("sys.exit") as mock_exit:
        with patch("imagesearch.__main__.PARSER") as mock_parser:
            mock_parser.parse_args.side_effect = KeyboardInterrupt()

            main([])

        mock_exit.assert_called_once_with(ExitStatus.ERROR_CTRL_C)

    captured_err = capsys.readouterr().err
    assert "interrupted" in captured_err


def test_image_search_exception_exit(capsys) -> None:  # type: ignore
    """Test that the raising of an ImageSearchException exits with the right exit code."""
    with patch("sys.exit") as mock_exit:
        main(["imagesearch", "dupe", str(NON_EXISTANT_FILE)])

        mock_exit.assert_called_once_with(ExitStatus.ERROR)

    captured_err = capsys.readouterr().err
    # this assertion is coupled with the text of the error message, so be careful if that changes.
    assert str(NON_EXISTANT_FILE) in captured_err
