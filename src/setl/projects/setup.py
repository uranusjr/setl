__all__ = ["ProjectSetupMixin"]

import os
import pathlib
import subprocess

from typing import Sequence

from .base import BaseProject
from .build import BuildEnv


def _get_setuppy_args(root: pathlib.Path) -> Sequence[str]:
    """Get an entry point to invoke Setuptools.

    * If there's a setup.py file, just use it.
    * If setup.py does not exist, but setup.cfg does. This is a more "modern"
      setup; invoke Setuptools with a stub and let Setuptools do the rest.
    """
    if root.joinpath("setup.py").exists():
        return ["setup.py"]
    if not root.joinpath("setup.cfg").is_file():
        raise FileNotFoundError("setup.py")
    return ["-c", "from setuptools import setup; setup()"]


class ProjectSetupMixin(BaseProject):
    def setuppy(
        self, env: BuildEnv, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess:
        cmd = [
            os.fspath(env.interpreter),
            *_get_setuppy_args(self.root),
            *args,
        ]
        return subprocess.run(cmd, cwd=self.root, check=check)
