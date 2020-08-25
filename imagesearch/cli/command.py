"""CLI commands."""
from __future__ import annotations

import sys
from abc import abstractmethod, ABCMeta
import json
from argparse import Namespace
from typing import Generator, List, Generic, TypeVar, Any, Callable

from imagesearch import Dupe, ImageDiff
from imagesearch.exceptions import UnknownFormatException
from imagesearch.cli.format import Format


ItemT = TypeVar("ItemT")


class _FakeGenericABCMeta(ABCMeta):
    """Allows for generic subtyping"""

    def __getitem__(cls, item: Any) -> ABCMeta:
        """
        Generic subscript hack, like Foo[Bar].

        TODO Is this necessary? Like, do I need to do this to generically subclass?
        """
        return cls


class Command(Generic[ItemT], metaclass=_FakeGenericABCMeta):
    """
    Abstract base class for running commands. Sets up subclass requirements for each output format.
    """

    # If a new format is to be supported, add it to the Format enum, create a new abstract class
    # method, and then add that method to the map in output_function_by_format.

    @classmethod
    def output_function_by_format(
        cls, format_: Format
    ) -> Callable[[Namespace, Generator[ItemT, None, None]], str]:
        """
        Selects an output function based on format. Raises an UnknownFormatException if format is
        not known.
        """
        formats = {
            Format.JSON: cls.json_output,
            Format.TEXT: cls.text_output,
        }
        if format_ in formats:
            return formats[format_]

        raise UnknownFormatException(f"No format with name {format_}.")

    @classmethod
    @abstractmethod
    def _generate(cls, args: Namespace) -> Generator[ItemT, None, None]:
        """Generate items for consumption by the output methods."""
        raise NotImplementedError("Cannot call this method on base class.")

    @classmethod
    @abstractmethod
    def json_output(cls, args: Namespace, items: Generator[ItemT, None, None]) -> str:
        """Produce a json string for output of the items"""
        raise NotImplementedError("Cannot call this method on base class.")

    @classmethod
    @abstractmethod
    def text_output(cls, args: Namespace, items: Generator[ItemT, None, None]) -> str:
        """Produce a text string for output of the items"""
        raise NotImplementedError("Cannot call this method on base class.")

    @classmethod
    def run(cls, args: Namespace) -> None:
        """Run the command, generating any items and output them to stdout."""
        items: Generator[ItemT, None, None] = cls._generate(args)
        format_function = cls.output_function_by_format(args.format)
        sys.stdout.write(format_function(args=args, items=items) + "\n")  # type: ignore


class DupeCommand(Command[Dupe]):
    """Run the dupe finding command."""

    @classmethod
    def json_output(cls, args: Namespace, items: Generator[Dupe, None, None]) -> str:
        """Outputs a json format string."""
        return json.dumps(
            {
                "algorithm": args.algorithm.algo_name,
                "dupes": [
                    {
                        "image_hash": str(dupe.image_hash),
                        "paths": [str(path.resolve()) for path in dupe.paths],
                    }
                    for dupe in items
                ],
            },
            indent=2,
        )

    @classmethod
    def text_output(cls, args: Namespace, items: Generator[Dupe, None, None]) -> str:
        """Outputs a text format string."""
        text_lines: List[str] = []
        for dupe in items:
            text_lines.append(str(dupe.image_hash))
            for path in dupe.paths:
                text_lines.append(str(path.resolve()))
        return "\n".join(text_lines)

    @classmethod
    def _generate(cls, args: Namespace) -> Generator[Dupe, None, None]:
        """Call the compare function with parsed args."""
        return Dupe.find(
            search_paths=args.search_paths,
            algorithm=args.algorithm,
            algo_params=args.algo_params,
        )


class CompareCommand(Command[ImageDiff]):
    """Run the compare command."""

    @classmethod
    def json_output(
        cls, args: Namespace, items: Generator[ImageDiff, None, None]
    ) -> str:
        """Outputs a json format string."""
        return json.dumps(
            {
                "reference_path": str(args.ref_path.resolve()),
                "algorithm": args.algorithm.algo_name,
                "diffs": [
                    {"diff": image_diff.diff, "path": str(image_diff.path.resolve())}
                    for image_diff in items
                ],
            },
            indent=2,
        )

    @classmethod
    def text_output(
        cls, args: Namespace, items: Generator[ImageDiff, None, None]
    ) -> str:
        """Outputs a text format string."""
        text_lines: List[str] = [str(args.ref_path.resolve())]
        for image_diff in items:
            text_lines.append(f"{image_diff.diff}\t{image_diff.path.resolve()}")
        return "\n".join(text_lines)

    @classmethod
    def _generate(cls, args: Namespace) -> Generator[ImageDiff, None, None]:
        """Call the compare function with parsed args."""
        return ImageDiff.compare(
            ref_path=args.ref_path,
            search_paths=args.search_paths,
            algorithm=args.algorithm,
            algo_params=args.algo_params,
            threshold=args.threshold,
            stop_on_first_match=args.stop_on_first_match,
        )
