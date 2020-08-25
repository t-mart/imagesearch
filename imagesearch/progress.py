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

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        iterable=None,
        desc=None,
        # total=None,
        leave=True,
        file=None,
        ncols=None,
        # mininterval=0.1,
        maxinterval=10.0,
        miniters=None,
        ascii=None,  # pylint: disable=redefined-builtin
        disable=False,
        # unit='it',
        unit_scale=False,
        dynamic_ncols=False,
        smoothing=0.3,
        bar_format=None,
        initial=0,
        position=None,
        postfix=None,
        unit_divisor=1000,
        write_bytes=None,
        lock_args=None,
        nrows=None,
        gui=False,
        files_hashed=0,
        files_skipped=0,
        last_file=None,
        **kwargs
    ):
        super().__init__(
            iterable=iterable,
            desc=desc,
            total=0,
            leave=leave,
            file=file,
            ncols=ncols,
            mininterval=1.0,
            maxinterval=maxinterval,
            miniters=miniters,
            ascii=ascii,
            disable=disable,
            unit=' files',
            unit_scale=unit_scale,
            dynamic_ncols=dynamic_ncols,
            smoothing=smoothing,
            bar_format=bar_format,
            initial=initial,
            position=position,
            postfix=postfix,
            unit_divisor=unit_divisor,
            write_bytes=write_bytes,
            lock_args=lock_args,
            nrows=nrows,
            gui=gui,
            **kwargs
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
            hashed=self.files_hashed,
            skipped=self.files_skipped,
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
