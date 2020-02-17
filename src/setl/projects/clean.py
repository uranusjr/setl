__all__ = ["ProjectCleanMixin"]

import json
import os
import shutil
import subprocess

from typing import Dict, Iterator, List, Optional

from packaging.utils import canonicalize_name

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


def _iter_egg_infos(entries: List[Dict[str, str]], name: str) -> Iterator[str]:
    for entry in entries:
        if name != canonicalize_name(entry["name"]):
            continue
        location = entry["location"]
        for filename in os.listdir(location):
            stem, ext = os.path.splitext(filename)
            if canonicalize_name(stem) == name and ext == ".egg-info":
                yield os.path.join(location, filename)


class ProjectCleanMixin(ProjectDevelopMixin):
    def _clean_egg_info(self, env: BuildEnv):
        name = _get_name(self.iter_metadata_for_development(env))
        if not name:
            return

        args = [
            os.fspath(env.interpreter),
            "-m",
            "pip",
            "list",
            "--format=json",
            "--editable",
            "--verbose",  # Needed for the "location" field. (pypa/pip#7664)
        ]
        output = subprocess.check_output(args, text=True)
        entries = json.loads(output)
        for path in _iter_egg_infos(entries, canonicalize_name(name)):
            shutil.rmtree(path)

    def clean(self, env: BuildEnv):
        # Clean up the built .egg-info. This is probably a good idea.
        # https://github.com/pypa/setuptools/issues/1347
        self._clean_egg_info(env)

        self.setuppy(env, "clean", "--all")

        # We don't just clean up here because the build environment is still
        # active, and the caller might want to use it after the call. Set a
        # flag so it is deleted when the context exits instead.
        env.mark_for_cleanup()
