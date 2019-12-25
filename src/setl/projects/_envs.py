# THIS FILE IS VENDORED FROM PYEM, only removing references to virtenv.
# DO NOT MODIFY THIS DIRECTLY OTHERWISE.

__all__ = [
    "EnvironmentCreationError",
    "PyUnavailable",
    "get_interpreter_quintuplet",
    "resolve_python",
]

import dataclasses
import os
import pathlib
import re
import shutil
import subprocess
import typing


class PyUnavailable(Exception):
    pass


def _get_command_output(args: typing.Sequence[str]) -> str:
    return subprocess.check_output(args, text=True).strip()


_PY_VER_RE = re.compile(
    r"""
    ^
    (\d+)           # Major.
    (:?\.(\d+))?    # Dot + Minor.
    (:?\-(32|64))?  # Dash + either 32 or 64.
    $
    """,
    re.VERBOSE,
)


def _find_python_with_py(python: str) -> typing.Optional[pathlib.Path]:
    py = shutil.which("py")
    if not py:
        raise PyUnavailable()
    code = "import sys; print(sys.executable)"
    try:
        output = _get_command_output([py, f"-{python}", "-c", code])
    except subprocess.CalledProcessError:
        return None
    if not output:
        return None
    return pathlib.Path(output).resolve()


def resolve_python(python: str) -> typing.Optional[pathlib.Path]:
    if _PY_VER_RE.match(python):
        return _find_python_with_py(python)
    resolved = shutil.which(python)
    if resolved:
        return pathlib.Path(resolved)
    path = pathlib.Path(python)
    if path.is_file():
        return path
    return None


# The prefix part is adopted from Virtualenv's approach. This allows us to find
# the most "base" prefix as possible, going through both virtualenv and venv
# boundaries. In particular `real_prefix` must be tried first since virtualenv
# does not preserve any other values.
# https://github.com/pypa/virtualenv/blob/16.7.7/virtualenv.py#L1419-L1426
_VENV_NAME_CODE = """
from __future__ import print_function

import hashlib
import sys
import sysconfig
import platform

try:
    prefix = sys.real_prefix
except AttributeError:
    try:
        prefix = sys.base_prefix
    except AttributeError:
        prefix = sys.prefix

prefix = prefix.encode(sys.getfilesystemencoding(), "ignore")

print("{impl}-{vers}-{syst}-{plat}-{hash}".format(
    impl=platform.python_implementation(),
    vers=sysconfig.get_python_version(),
    syst=platform.uname()[0],
    plat=sysconfig.get_platform().split("-")[-1],
    hash=hashlib.sha256(prefix).hexdigest()[:8],
).lower())
"""


def get_interpreter_quintuplet(python: typing.Union[str, pathlib.Path]) -> str:
    """Build a unique identifier for the interpreter to place the venv.

    This is done by asking the interpreter to format a string containing the
    following parts, lowercased and joined with `-` (dash):

    * Python inplementation.
    * Python version (major.minor).
    * Plarform name.
    * Processor type.
    * A 8-char hash of the interpreter prefix for disambiguation.

    Example: `cpython-3.7-darwin-x86_64-3d3725a6`.
    """
    return _get_command_output([os.fspath(python), "-c", _VENV_NAME_CODE])


@dataclasses.dataclass()
class EnvironmentCreationError(Exception):
    context: Exception
