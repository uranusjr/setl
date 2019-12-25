__all__ = ["ProjectPEP517HookCallerMixin"]

import functools
import pathlib

import pep517.wrappers

from .build import BuildEnv, ProjectBuildManagementMixin
from .meta import ProjectMetadataMixin


class ProjectPEP517HookCallerMixin(
    ProjectBuildManagementMixin, ProjectMetadataMixin
):
    @functools.cached_property  # type: ignore  # Mypy does not have this yet.
    def hooks(self) -> pep517.wrappers.Pep517HookCaller:
        return pep517.wrappers.Pep517HookCaller(
            self.root, self.build_backend, self.backend_path
        )

    def build_sdist(self, env: BuildEnv) -> pathlib.Path:
        requirements = self.hooks.get_requires_for_build_sdist()
        self.install_build_requirements(env, requirements)
        target = self.hooks.build_sdist(self.root.joinpath("dist"))
        return self.root.joinpath("dist", target)

    def build_wheel(self, env: BuildEnv) -> pathlib.Path:
        requirements = self.hooks.get_requires_for_build_wheel()
        self.install_build_requirements(env, requirements)
        target = self.hooks.build_wheel(self.root.joinpath("dist"))
        return self.root.joinpath("dist", target)
