"""
Returns the similiarity between a reference image and a set of other images.
"""
__version__ = '0.1.3'

from .fingerprint import Algorithm
from . import exceptions
from .search import search, ImageDiff
