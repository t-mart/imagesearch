"""Helper for tqdm progress bars."""
from __future__ import annotations

from typing import Dict, Optional, Union
from collections import OrderedDict as odict
from pathlib import Path

from tqdm import tqdm


class SearchProgressBar(tqdm):
    """A manager for a tdqm progress bar."""

    files_hashed: int
    files_skipped: int
    last_file: Optional[Path]
    pbar: tqdm

    def __init__(
        self,
        files_hashed: int = 0,
        files_skipped: int = 0,
        last_file: Optional[Path] = None,
    ):
        super().__init__(
            total=0, mininterval=1.0, unit=" files",
        )
        self.files_hashed = files_hashed
        self.files_skipped = files_skipped
        self.last_file = last_file

    def add_to_total(self, count: int = 1, interval: int = 10) -> None:
        """Increment the total and refresh the bar if total is a factor of interval."""
        self.total += count
        if self.total % interval == 0:
            self.refresh(nolock=True)

    def to_dict(self) -> Dict[str, Union[str, int]]:
        """Returns a dictionary of key value pairs for this object"""
        prog_dict: Dict[str, Union[str, int]] = odict(
            hashed=self.files_hashed, skipped=self.files_skipped,
        )

        if self.last_file is not None:
            prog_dict["last_file"] = str(self.last_file)

        return prog_dict

    def add_skip(self, path: Path) -> None:
        """Increments skips, sets the last file, and calls set_postfix on the provided tqdm."""
        self.last_file = path
        self.files_skipped += 1

        self.set_postfix(ordered_dict=self.to_dict(), refresh=False)
        self.update(1)

    def add_hash(self, path: Path) -> None:
        """Increments hashes, sets the last file, and calls set_postfix on the provided tqdm."""
        self.last_file = path
        self.files_hashed += 1

        self.set_postfix(ordered_dict=self.to_dict(), refresh=False)
        self.update(1)
