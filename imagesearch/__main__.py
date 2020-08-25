"""The main entry point. Invoke as `imagesearch' or `python -m imagesearch`."""
import sys
from typing import List

from imagesearch.status import ExitStatus
from imagesearch.exceptions import ImageSearchException
from imagesearch.cli import PARSER


def main(args: List[str] = sys.argv) -> None:  # pylint: disable=dangerous-default-value
    """Entry point function."""
    try:
        parsed_args = PARSER.parse_args(args[1:])
        parsed_args.command(args=parsed_args)
    except ImageSearchException as exc:
        sys.stderr.write(f"imagesearch: error: {exc}\n")
        exit_status = ExitStatus.ERROR
    except KeyboardInterrupt:
        sys.stderr.write("imagesearch: error: interrupted\n")
        exit_status = ExitStatus.ERROR_CTRL_C
    else:
        exit_status = ExitStatus.SUCCESS

    sys.exit(exit_status.value)


if __name__ == "__main__":
    main()  # pragma: no cover
