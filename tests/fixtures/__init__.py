"""Helper fixtures for the test images directory"""
from pathlib import Path

# Various directories and counts.
TEST_IMAGE_DIR = Path(__file__).parent / "images"
TEST_IMAGE_DIR_IMAGE_COUNT = 10

TEST_IMAGE_SUBDIR_0 = TEST_IMAGE_DIR / "subdir0"
TEST_IMAGE_SUBDIR_0_IMAGE_COUNT = 5

TEST_IMAGE_SUBDIR_1_0 = TEST_IMAGE_DIR / "subdir0" / "subdir1-0"
TEST_IMAGE_SUBDIR_1_0_IMAGE_COUNT = 3

TEST_IMAGE_SUBDIR_1_1 = TEST_IMAGE_DIR / "subdir0" / "subdir1-1"
TEST_IMAGE_SUBDIR_1_1_IMAGE_COUNT = 2

# Various image files.
REF_IMAGE = TEST_IMAGE_DIR / "en.wikipedia.org-Macaca_nigra_self-portrait_large.jpg"
IMAGE_NOT_IN_SUBDIR_1_1 = REF_IMAGE
IMAGE_IN_SUBDIR_1_1 = (
    TEST_IMAGE_SUBDIR_1_1 / "en.wikipedia.org-Actinoscyphia_aurelia_1.jpg"
)
DUPE_PATH_A = TEST_IMAGE_DIR / "en.wikipedia.org-Macaca_nigra_self-portrait_large.jpg"
DUPE_PATH_B = (
    TEST_IMAGE_DIR
    / "subdir0"
    / "en.wikipedia.org-Macaca_nigra_self-portrait_large dupe.jpg"
)
NON_DUPE_PATH = (
    TEST_IMAGE_DIR
    / "en.wikipedia.org-Lauren_Mitchell,_41st_AG_World_Championship,_2009_(full_tone_blur).jpg"
)
NON_EXISTANT_FILE = TEST_IMAGE_DIR / "does-not-exist"
UNSUPPORTED_IMAGE = TEST_IMAGE_DIR / "not-an-image.txt"
