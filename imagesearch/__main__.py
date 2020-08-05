"""Run the module."""
import sys

from .config import CONFIG
from .search import search
from .fingerprint import Algorithm
from .exceptions import ImageSearchException


def main() -> None:
    """Run the image matcher."""
    try:
        image_diffs = search(
            ref_path=CONFIG.ref_path,
            search_paths=CONFIG.search_paths,
            algorithm=Algorithm.from_name(CONFIG.algorithm),
            threshold=CONFIG.threshold,
            stop_on_first_match=CONFIG.stop_on_first_match
        )

        for image_diff in image_diffs:
            print(image_diff.output_line())
    except ImageSearchException as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(True)


if __name__ == '__main__':
    main()
