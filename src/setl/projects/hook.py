__all__ = ["ProjectPEP517HookCallerMixin"]

import logging
import pathlib
import re

import cached_property
import pep517.wrappers

from .build import BuildEnv, ProjectBuildManagementMixin
from .meta import ProjectMetadataMixin


logger = logging.getLogger(__name__)

PYPROJECT_TOML_PATTERN = re.compile(r"^[^/]+/pyproject\.toml$")


class ProjectPEP517HookCallerMixin(
    ProjectBuildManagementMixin, ProjectMetadataMixin
):
    @cached_property.cached_property
    def hooks(self) -> pep517.wrappers.Pep517HookCaller:
        return pep517.wrappers.Pep517HookCaller(
            self.root,
            self.build_backend,
            self.backend_path,
            runner=pep517.wrappers.quiet_subprocess_runner,
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
