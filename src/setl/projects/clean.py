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


# TODO: Reliying on Setuptools being present in the isolated build
# environment. This is fine since Setl is strictly a Setuptools frontend, but
# for a generic PEP 517 frontend we need another way to find the .egg-info
# directory. The .egg-link thing is very tricky though...
_GET_EGG_INFO_LOCATION_CODE = """
import os
import sys
import pkg_resources

try:
    dist = pkg_resources.get_distribution(sys.argv[1])
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

        args = [
            os.fspath(env.interpreter),
            "-c",
            _GET_EGG_INFO_LOCATION_CODE,
            name,
        ]
        info = subprocess.check_output(args, text=True).strip()

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
