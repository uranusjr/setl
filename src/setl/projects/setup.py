__all__ = ["ProjectSetupMixin"]

import os
import subprocess

from typing import Sequence

from .base import BaseProject
from .build import BuildEnv


class ProjectSetupMixin(BaseProject):
    def _setuppy(self, env: BuildEnv, *args: str):
        # TODO: Don't assume setup.py exists. Provide a stub if not.
        subprocess.check_call(
            [os.fspath(env.interpreter), "setup.py", *args], cwd=self.root
        )

    def build(self, env: BuildEnv, steps: Sequence[str]):
        self._setuppy(env, *steps)

    def clean(self, env: BuildEnv):
        self._setuppy(env, "clean")

    def install_for_development(self, env: BuildEnv):
        self._setuppy(env, "develop")
