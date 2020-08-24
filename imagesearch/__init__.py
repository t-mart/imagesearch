"""
Returns the similiarity between a reference image and a set of other images.
"""
__version__ = "0.3.0"

from imagesearch.fingerprint import Algorithm, ImageFingerprint
from imagesearch import exceptions
from imagesearch.compare import ImageDiff
from imagesearch.dupe import Dupe
