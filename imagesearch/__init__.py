"""
Returns the similiarity between a reference image and a set of other images.
"""
__version__ = "0.2.1"

from .fingerprint import Algorithm, ImageFingerprint
from . import exceptions
from .compare import ImageDiff
from .dupe import Dupe
