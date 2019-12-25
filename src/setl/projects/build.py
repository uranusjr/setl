from __future__ import annotations

__all__ = ["BuildEnv", "ProjectBuildManagementMixin"]

import dataclasses
import os
import pathlib
import subprocess
import sysconfig

from typing import Optional, Sequence

from ._envs import get_interpreter_quintuplet, resolve_python
from .meta import ProjectMetadataMixin


@dataclasses.dataclass()
class InterpreterNotFound(Exception):
    spec: str


_ENV_CONTAINER_NAME = ".isoenvs"


def _join_paths(*paths: Optional[str]) -> str:
    return os.pathsep.join(path for path in paths if path)


@dataclasses.dataclass()
class BuildEnv:
    """Context manager to install build deps in a simple temporary environment.

    Based on ``pep517.envbuild.BuildEnvironment``, which is in turn based on
    pip's implementation. The difference here is that we don't clean up the
    environment directory, and actually reuse it across builds.
    """

    root: pathlib.Path
    interpreter: pathlib.Path

    def __enter__(self) -> BuildEnv:
        self.backenv = {k: os.environ.get(k) for k in ["PATH", "PYTHONPATH"]}

        base = os.fspath(self.root)
        paths = sysconfig.get_paths(vars={"base": base, "platbase": base})

        os.environ["PATH"] = _join_paths(
            paths["scripts"], self.backenv["PATH"] or os.defpath
        )
        os.environ["PYTHONPATH"] = _join_paths(
            paths["purelib"], paths["platlib"], self.backenv["PYTHONPATH"]
        )

        return self

    def __exit__(self, etype, eval, etb):
        for k, v in self.backenv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class ProjectBuildManagementMixin(ProjectMetadataMixin):
    def ensure_build_envdir(self, interpreter_spec: str) -> BuildEnv:
        """Ensure an isolated environment exists for build.

        :param interpreter_spec: Specification of the base interpreter.
        :returns: A context manager to control build setup/teardown.
        """
        python = resolve_python(interpreter_spec)
        if not python:
            raise InterpreterNotFound(interpreter_spec)
        quintuplet = get_interpreter_quintuplet(python)
        env_dir = self.root.joinpath("build", _ENV_CONTAINER_NAME, quintuplet)
        env_dir.mkdir(exist_ok=True, parents=True)
        return BuildEnv(env_dir, python)

    def install_build_requirements(self, env: BuildEnv, reqs: Sequence[str]):
        if not reqs:
            return
        args = [
            os.fspath(env.interpreter),
            "-m",
            "pip",
            "install",
            "--prefix",
            os.fspath(env.root),
            *reqs,
        ]
        subprocess.check_call(args)

    def ensure_build_requirements(self, env: BuildEnv):
        """Ensure the given environment has build requirements populated.
        """
        self.install_build_requirements(env, self.build_requirements)
        # TODO: We might need to install things to build for development?
        # PEP 517 does not cover this yet, so we just do nothing for now.
