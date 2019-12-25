__all__ = ["ProjectSetupMixin"]

import subprocess
import sys


class ProjectSetupMixin:
    def _setuppy(self, *args):
        # TODO: Don't assume setup.py exists. Provide a stub if not.
        subprocess.check_call(
            [sys.executable, "setup.py", *args], cwd=self.root
        )

    def build(self, steps):
        self._setuppy(*steps)

    def clean(self):
        self._setuppy("clean")

    def install_for_development(self):
        self._setuppy("develop")
