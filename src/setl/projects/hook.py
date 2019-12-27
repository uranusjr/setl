__all__ = ["ProjectPEP517HookCallerMixin"]

import functools
import logging
import pathlib
import re
import tarfile

import pep517.wrappers

from .build import BuildEnv, ProjectBuildManagementMixin
from .meta import ProjectMetadataMixin


logger = logging.getLogger(__name__)

PYPROJECT_TOML_PATTERN = re.compile(r"^[^/]+/pyproject\.toml$")


class ProjectPEP517HookCallerMixin(
    ProjectBuildManagementMixin, ProjectMetadataMixin
):
    @functools.cached_property  # type: ignore  # Mypy does not have this yet.
    def hooks(self) -> pep517.wrappers.Pep517HookCaller:
        return pep517.wrappers.Pep517HookCaller(
            self.root,
            self.build_backend,
            self.backend_path,
            runner=pep517.wrappers.quiet_subprocess_runner,
        )

    def _warn_if_pyproject_toml_not_present(self, target: str):
        with tarfile.open(self.root.joinpath("dist", target)) as tf:
            if any(PYPROJECT_TOML_PATTERN.match(n) for n in tf.getnames()):
                return
        logger.warn(
            "pyproject.toml not found in `%s`. Add the following to "
            "your MANIFEST.in:\n\n    include pyproject.toml\n\n"
            "See: https://github.com/pypa/setuptools/issues/1632\n",
            target,
        )

    def build_sdist(self, env: BuildEnv) -> pathlib.Path:
        requirements = self.hooks.get_requires_for_build_sdist()
        self.install_build_requirements(env, requirements)
        target = self.hooks.build_sdist(self.root.joinpath("dist"))
        self._warn_if_pyproject_toml_not_present(target)
        return self.root.joinpath("dist", target)

    def build_wheel(self, env: BuildEnv) -> pathlib.Path:
        requirements = self.hooks.get_requires_for_build_wheel()
        self.install_build_requirements(env, requirements)
        target = self.hooks.build_wheel(self.root.joinpath("dist"))
        return self.root.joinpath("dist", target)
