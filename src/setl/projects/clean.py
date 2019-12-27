__all__ = ["ProjectCleanMixin"]

import os
import shutil
import subprocess

from typing import Iterator, Optional

from .build import BuildEnv
from .dev import ProjectDevelopMixin


def _get_name(f: Iterator[str]) -> Optional[str]:
    for line in f:
        if ":" not in line:  # End of metadata.
            break
        k, v = line.strip().split(":", 1)
        if k.lower() == "name":
            return v.strip()
    return None


_GET_EGG_INFO_LOCATION_CODE = """
import os
import pkg_resources

name = os.environ["SELT_GET_EGG_INFO_LOCATION_NAME"]
try:
    dist = pkg_resources.get_distribution(name)
except pkg_resources.DistributionNotFound:
    pass
else:
    print(getattr(dist, "egg_info", ""))
"""


class ProjectCleanMixin(ProjectDevelopMixin):
    def _clean_egg_info(self, env: BuildEnv):
        name = _get_name(self.iter_metadata_for_development(env))
        if not name:
            return

        environ = os.environ.copy()
        environ["SELT_GET_EGG_INFO_LOCATION_NAME"] = name
        args = [
            os.fspath(env.interpreter),
            "-c",
            _GET_EGG_INFO_LOCATION_CODE,
        ]
        info = subprocess.check_output(args, env=environ, text=True).strip()

        if not info or not os.path.isdir(info):
            return
        shutil.rmtree(info)

    def clean(self, env: BuildEnv):
        # Clean up the built .egg-info. This is probably a good idea.
        # https://github.com/pypa/setuptools/issues/1347
        self._clean_egg_info(env)

        self.setuppy(env, "clean", "--all")

        # We don't just clean up here because the build environment is still
        # active, and the caller might want to use it after the call. Set a
        # flag so it is deleted when the context exits instead.
        env.mark_for_cleanup()
