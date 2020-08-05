"""Exceptions."""


class ImageSearchException(Exception):
    """Parent exception"""


class DoesNotExistException(ImageSearchException):
    """Indicates that a path does not exist."""


class FileNotReadableException(ImageSearchException):
    """Indicates the path is not a file (for source images)."""


class UnsupportedImageException(ImageSearchException):
    """Indicates that the file is not supported for decoding."""


class NotSearchableException(ImageSearchException):
    """Indicates that a path is not a file or directory."""


class ThresholdException(ImageSearchException):
    """Indicates the threshold is invalid."""


class UnknownAlgorithmException(ImageSearchException):
    """Indicates the specified algorithm does not name a known algorithm."""
