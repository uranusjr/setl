__all__ = ["ProjectDevelopMixin"]

import os
import subprocess

from typing import Collection, Iterator, Optional

import packaging.markers
import packaging.requirements

from .build import BuildEnv
from .hook import ProjectPEP517HookCallerMixin
from .setup import ProjectSetupMixin


def _evaluate_marker(
    marker: Optional[packaging.markers.Marker], extras: Collection[str]
) -> bool:
    if not marker:
        return True
    if marker.evaluate({"extra": ""}):
        return True
    return any(marker.evaluate({"extra": e}) for e in extras)


def _iter_requirements(
    f: Iterator[str], key: str, extras: Collection[str]
) -> Iterator[packaging.requirements.Requirement]:
    """Hand-rolled implementation to read ``*.dist-info/METADATA``.

    I don't want to pull in distlib for this (it's not even good at this). The
    wheel format is quite well-documented anyway. This is almost too simple
    and I'm quite sure I'm missing edge cases, but let's fix them when needed.
    """
    key = key.lower()
    for line in f:
        if ":" not in line:  # End of metadata.
            return
        k, v = line.strip().split(":", 1)
        if k.lower() != key:
            continue
        try:
            requirement = packaging.requirements.Requirement(v)
        except ValueError:
            continue
        if not requirement.marker:
            yield requirement
            continue
        if _evaluate_marker(requirement.marker, extras):
            yield requirement


class ProjectDevelopMixin(ProjectPEP517HookCallerMixin, ProjectSetupMixin):
    def install_for_development(self, env: BuildEnv):
        """Install the project for development.

        This is a mis-mash between `setup.py develop` and `pip install -e .`
        because we want to have the best of both worlds. Setuptools installs
        egg-info distributions, which is less than ideal. pip, on the other
        hand, does not let us reuse our own build environment, and also
        creates ``pip-wheel-metadata`` ("fixed" in pip 20.0, but still).

        Our own solution...

        1. Installs build requirements for wheel (see next step).
        2. Call ``prepare_metadata_for_build_wheel``. The result would tell us
           what run-time requirements this project has.
        3. Install run-time requirements with pip, so they are installed as
           modern distributions (dist-info).
        4. Call `setup.py develop --no-deps` so we install the package itself
           without pip machinery.

        The wheel metadata generated in step 2 are stored in the build
        environment, so it is more easily ignored and cleaned up.
        """
        requirements = self.hooks.get_requires_for_build_wheel()
        self.install_build_requirements(env, requirements)

        container = env.root.joinpath("setl-wheel-metadata")
        target = self.hooks.prepare_metadata_for_build_wheel(container)
        with container.joinpath(target, "METADATA").open(encoding="utf8") as f:
            requirements = list(_iter_requirements(f, "requires-dist", []))

        args = [
            os.fspath(env.interpreter),
            "-m",
            "pip",
            "install",
            *(str(r) for r in requirements),
        ]
        subprocess.check_call(args, cwd=self.root)

        self.setuppy(env, "develop", "--no-deps")
