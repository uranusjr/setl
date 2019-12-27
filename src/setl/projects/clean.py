__all__ = ["ProjectCleanMixin"]

import os
import shutil
import subprocess

from typing import Iterator, Optional

import pkg_resources

from .build import BuildEnv
from .dev import ProjectDevelopMixin


def _get_distribution(
    f: Iterator[str],
) -> Optional[pkg_resources.Distribution]:
    for line in f:
        if ":" not in line:  # End of metadata.
            break
        k, v = line.strip().split(":", 1)
        if k.lower() != "name":
            continue
        try:
            return pkg_resources.get_distribution(v.strip())
        except pkg_resources.DistributionNotFound:
            continue
    return None


_CHECK_IN_PATH_CODE = """
import os
import sys

location = os.environ["SETL_IS_INSTALLED_FOR_DEV_LOCATION"]
for path in sys.path:
    if os.path.commonprefix([path, location]) == path:
        print("regular")
        break
else:
    print("develop")
"""


class ProjectCleanMixin(ProjectDevelopMixin):
    def _is_installed_for_dev(self, env: BuildEnv, path: str) -> bool:
        args = [
            os.fspath(env.interpreter),
            "-c",
            _CHECK_IN_PATH_CODE,
        ]
        environ = os.environ.copy()
        environ["SETL_IS_INSTALLED_FOR_DEV_LOCATION"] = path
        output = subprocess.check_output(args, env=environ, text=True).strip()

        return output == "develop"

    def _clean_egg_info(self, env: BuildEnv, dist: pkg_resources.Distribution):
        egg_info = getattr(dist, "egg_info", None)
        if not egg_info or not os.path.exists(egg_info):
            return

        # Uninstall the develop build (otherwise removing .egg-info would
        # result in a broken environment).
        if self._is_installed_for_dev(env, os.fspath(dist.location)):
            args = [
                os.fspath(env.interpreter),
                "-m",
                "pip",
                "uninstall",
                "--yes",
                dist.project_name,
            ]
            subprocess.check_call(args)

        shutil.rmtree(egg_info)

    def clean(self, env: BuildEnv):
        # Clean up the built .egg-info. This is probably a good idea.
        # https://github.com/pypa/setuptools/issues/1347
        dist = _get_distribution(self.iter_metadata_for_development(env))
        if dist:
            self._clean_egg_info(env, dist)

        self.setuppy(env, "--quiet", "clean", "--all")

        # We don't just clean up here because the build environment is still
        # active, and the caller might want to use it after the call. Set a
        # flag so it is deleted when the context exits instead.
        env.mark_for_cleanup()
