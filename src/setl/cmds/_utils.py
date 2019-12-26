import os
import pathlib
import subprocess
import sys

from typing import Union


def twine(c: str, *args: Union[str, pathlib.Path]):
    cmd = [sys.executable, "-m", "twine", c, *(os.fspath(a) for a in args)]
    subprocess.check_call(cmd)
