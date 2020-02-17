from __future__ import annotations

__all__ = ["BuildEnv", "ProjectBuildManagementMixin"]

import contextlib
import dataclasses
import json
import os
import pathlib
import shutil
import subprocess

from typing import Dict, Iterable, Iterator, Optional, Set

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from ._envs import get_interpreter_quintuplet, resolve_python
from .meta import ProjectMetadataMixin


@dataclasses.dataclass()
class InterpreterNotFound(Exception):
    spec: str


_ENV_CONTAINER_NAME = ".isoenvs"


_GET_PATHS_CODE = """
from __future__ import print_function

import json
import os
import sys
import sysconfig

base = sys.argv[1]
print(json.dumps(sysconfig.get_paths(vars={"base": base, "platbase": base})))
"""


def _get_env_paths(python: pathlib.Path, root: pathlib.Path) -> Dict[str, str]:
    args = [os.fspath(python), "-c", _GET_PATHS_CODE, os.fspath(root)]
    output = subprocess.check_output(args, text=True).strip()
    return json.loads(output)


def _environ_path_format(*paths: Optional[str]) -> str:
    return os.pathsep.join(path for path in paths if path)


@dataclasses.dataclass()
class BuildEnv:
    root: pathlib.Path
    interpreter: pathlib.Path
    libdirs: Set[pathlib.Path]

    def __post_init__(self):
        self._should_delete = False

    def mark_for_cleanup(self):
        self._should_delete = True


def _list_installed(env: BuildEnv) -> Dict[str, str]:
    """List versions of installed packages in the build environment.

    This only lists packages under the isolated environment prefix, NOT
    packages in the parent environment.

    Returns a `{canonical_name: version}` mapping.
    """
    args = [
        os.fspath(env.interpreter),
        "-m",
        "pip",
        "list",
        "--format=json",
        *(f"--path={p}" for p in env.libdirs),
    ]
    environ = os.environ.copy()
    environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "true"
    output = subprocess.check_output(args, env=environ, text=True).strip()
    return {
        canonicalize_name(e["name"]): e["version"]
        for e in json.loads(output)
        if "name" in e and "version" in e
    }


def _is_req_met(req: str, workingset: Dict[str, str]) -> bool:
    """Check whether a request requirement is met by given workingset.

    :param req: A PEP 508 requirement string.
    :param workingset: A `{canonical_name: version}` mapping (e.g. returned by
        `_list_installed`).
    """
    r = Requirement(req)
    try:
        version = workingset[canonicalize_name(r.name)]
    except KeyError:
        return False
    return not r.specifier or version in r.specifier


class ProjectBuildManagementMixin(ProjectMetadataMixin):
    @contextlib.contextmanager
    def ensure_build_envdir(self, spec: str) -> Iterator[BuildEnv]:
        """Ensure an isolated environment exists for build.

        Environment setup is based on ``pep517.envbuild.BuildEnvironment``,
        which is in turn based on pip's implementation. The difference is the
        environment in a non-temporary, predictable location, and not cleaned
        up on exit. It is actually reused across builds.

        :param spec: Specification of the base interpreter.
        :returns: A context manager to control build setup/teardown.
        """
        # Identify the Python interpreter to use.
        python = resolve_python(spec)
        if not python:
            raise InterpreterNotFound(spec)

        # Create isolated environment.
        quintuplet = get_interpreter_quintuplet(python)
        env_dir = self.root.joinpath("build", _ENV_CONTAINER_NAME, quintuplet)
        env_dir.mkdir(exist_ok=True, parents=True)

        # Set up environment variables so PEP 517 subprocess calls can find
        # dependencies in the isolated environment.
        backenv = {k: os.environ.get(k) for k in ["PATH", "PYTHONPATH"]}
        paths = _get_env_paths(python, env_dir)
        libdirs = {paths["purelib"], paths["platlib"]}
        os.environ["PATH"] = _environ_path_format(
            paths["scripts"], backenv["PATH"] or os.defpath
        )
        os.environ["PYTHONPATH"] = _environ_path_format(
            *libdirs, backenv["PYTHONPATH"]
        )

        env = BuildEnv(
            root=env_dir,
            interpreter=python,
            libdirs={pathlib.Path(p) for p in libdirs},
        )
        yield env

        # Restore environment variables.
        for k, v in backenv.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

        if getattr(env, "_should_delete", False):
            shutil.rmtree(env.root)

    def install_build_requirements(self, env: BuildEnv, reqs: Iterable[str]):
        reqs = [r for r in reqs if not _is_req_met(r, _list_installed(env))]
        if not reqs:
            return
        args = [
            os.fspath(env.interpreter),
            "-m",
            "pip",
            "install",
            "--ignore-installed",
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
