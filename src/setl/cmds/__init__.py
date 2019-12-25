__all__ = ["dispatch"]

import argparse
import logging
import pathlib
import sys

from typing import List, Optional

from setl._logging import configure_logging
from setl.projects import Project

from . import build, clean, develop


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python", required=True, help="Target Python executable",
    )

    subparsers = parser.add_subparsers()
    for sub in [build, clean, develop]:
        sub.get_parser(subparsers)

    return parser


class _ProjectNotFound(Exception):
    start: pathlib.Path


def _find_project() -> Project:
    start = pathlib.Path.cwd()
    for path in start.joinpath("__placeholder__").parents:
        if path.joinpath("pyproject.toml").is_file():
            return Project(path)
    raise _ProjectNotFound(start)


def dispatch(argv: Optional[List[str]]) -> int:
    configure_logging(logging.INFO)  # TODO: Make this configurable.

    if argv is None:
        argv = sys.argv
    opts = get_parser().parse_args(argv)

    project = _find_project()
    return opts.func(project, opts)
