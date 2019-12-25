__all__ = ["dispatch"]

import argparse
import logging
import os
import pathlib
import shutil
import sys

from typing import Any, Dict, List, Optional

from setl._logging import configure_logging
from setl.projects import Project

from . import build, clean, develop, dist, publish


def _find_active_venv_python() -> Optional[pathlib.Path]:
    """Find Python interpreter of the currently active virtual environment.

    * A virtual environment should be active (via ``VIRTUAL_ENV``).
    * The ``python`` command should resolve into an executable inside the
      virtual environment.
    """
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if not virtual_env:
        return None
    command = shutil.which("python")
    if not command:
        return None
    python = pathlib.Path(command)
    try:
        prefix = python.relative_to(virtual_env)
    except ValueError:
        return None
    if pathlib.Path(virtual_env, prefix).samefile(python):
        return python
    return None


def _find_installed_venv_python() -> Optional[pathlib.Path]:
    # Venv: sys.prefix should be different from sys.base_prefix.
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return pathlib.Path(sys.executable)
    # Virtualenv: sys.real_prefix should be set.
    if hasattr(sys, "real_prefix"):
        return pathlib.Path(sys.executable)
    # Nothing is set, this is global.
    return None


def _get_python_kwargs() -> Dict[str, Any]:
    """Additional flags for the ``--python`` option.

    * If the ``SETL_PYTHON`` environment variable is set, use it as default.
    * If setl is running in a virtual environment context, default to the
      environment's ``python`` command.
    * If setl is installed in a virtual environment context, default to the
      environment's interpreter (i.e. ``sys.executable``).
    * Otherwise require an explicit ``--python`` argument.
    """
    default = (
        os.environ.get("SETL_PYTHON")
        or _find_active_venv_python()
        or _find_installed_venv_python()
    )
    if default:
        return {"default": os.fspath(default)}
    return {"required": True}


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python", help="Target Python executable", **_get_python_kwargs(),
    )

    subparsers = parser.add_subparsers()
    for sub in [build, clean, develop, dist, publish]:
        sub.get_parser(subparsers)  # type: ignore

    return parser


def _is_project_root(p: pathlib.Path) -> bool:
    """Check is a path marks a project's root directory.

    A valid project needs:

    * A pyproject.toml (because this is a PEP 517 tool).
    * Either setup.py or setup.cfg (or both) so we can invoke Setuptools.
    """
    if not p.joinpath("pyproject.toml").is_file():
        return False
    if p.joinpath("setup.py").is_file() or p.joinpath("setup.cfg").is_file():
        return True
    return False


class _ProjectNotFound(Exception):
    start: pathlib.Path


def _find_project() -> Project:
    start = pathlib.Path.cwd()
    for path in start.joinpath("__placeholder__").parents:
        if _is_project_root(path):
            return Project(path)
    raise _ProjectNotFound(start)


def dispatch(argv: Optional[List[str]]) -> int:
    configure_logging(logging.INFO)  # TODO: Make this configurable.
    opts = get_parser().parse_args(argv)
    project = _find_project()
    return opts.func(project, opts)
