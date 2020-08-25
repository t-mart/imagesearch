"""Exceptions."""


class ImageSearchException(Exception):
    """Parent exception"""


class ThresholdException(ImageSearchException):
    """Indicates the threshold is invalid."""


class UnknownAlgorithmException(ImageSearchException):
    """Indicates the specified algorithm does not name a known algorithm."""


class UnknownFormatException(ImageSearchException):
    """Indicates the specified format is unknown."""


class HashingException(ImageSearchException):
    """Indicates the path could not be hashed for some reason."""


class CLIException(ImageSearchException):
    """Indicates a problem parsing command line arguments."""


class BadAlgoParamsException(CLIException):
    """Indicates that the additional args passed to the algorithm are malformed."""


class DoesNotExistException(HashingException):
    """Indicates that a path does not exist."""


class NotReadableException(HashingException):
    """Indicates the path is not a file (for source images) or is not readable (permissions)."""


class UnsupportedImageException(HashingException):
    """Indicates that the file is not supported for decoding."""
