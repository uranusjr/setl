__all__ = ["dispatch"]

import argparse
import logging
import sys

from typing import List, Optional

from . import build
from ._logging import configure_logging


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python", required=True, help="Target Python executable",
    )

    subparsers = parser.add_subparsers()
    for sub in [build]:
        sub.get_parser(subparsers)

    return parser


def dispatch(argv: Optional[List[str]]) -> int:
    configure_logging(logging.INFO)  # TODO: Make this configurable.

    if argv is None:
        argv = sys.argv
    opts = get_parser().parse_args(argv)

    return opts.func(opts)
