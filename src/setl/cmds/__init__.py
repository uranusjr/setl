__all__ = ["dispatch"]

import argparse
import logging
import os
import pathlib
import sys

from typing import Any, Dict, List, Optional

from setl._logging import configure_logging
from setl.projects import Project

from . import build, clean, develop, dist, publish


def _get_python_kwargs() -> Dict[str, Any]:
    default_python = os.environ.get("SETL_PYTHON", "")
    if not default_python:
        return {"required": True}
    return {"default": default_python}


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python", help="Target Python executable", **_get_python_kwargs(),
    )

    subparsers = parser.add_subparsers()
    for sub in [build, clean, develop, dist, publish]:
        sub.get_parser(subparsers)  # type: ignore

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
