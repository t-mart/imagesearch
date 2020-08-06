"""Run the module."""
from __future__ import annotations
import sys
from typing import Optional

from .config import get_config, Config
from .search import search
from .fingerprint import Algorithm
from .exceptions import ImageSearchException


def main(config: Optional[Config] = None) -> None:
    """Run the image matcher."""
    if config is None:
        config = get_config()
    try:
        image_diffs = search(
            ref_path=config.ref_path,
            search_paths=config.search_paths,
            algorithm=Algorithm.from_name(config.algorithm),
            threshold=config.threshold,
            stop_on_first_match=config.stop_on_first_match
        )

        for image_diff in image_diffs:
            print(image_diff.output_line())
    except ImageSearchException as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(True)


if __name__ == '__main__':
    main()
