__all__ = ["ProjectMetadataMixin"]

import functools

import toml

from .base import BaseProject


_DEFAULT_BUILD_REQUIREMENTS = ["setuptools", "wheel"]
_DEFAULT_BUILD_SYSTEM = {
    "requires": _DEFAULT_BUILD_REQUIREMENTS,
    "build-backend": "setuptools.build_meta:__legacy__",
}


class ProjectMetadataMixin(BaseProject):
    @functools.cached_property  # type: ignore  # Mypy does not have this yet.
    def build_system(self):
        with self.root.joinpath("pyproject.toml").open() as f:
            data = toml.load(f)
        try:
            return data["build-system"]
        except KeyError:
            return _DEFAULT_BUILD_SYSTEM

    @property
    def build_requirements(self):
        return self.build_system.get("requires", _DEFAULT_BUILD_REQUIREMENTS)

    @property
    def build_backend(self):
        return self.build_system.get("build-backend", "setuptools.build_meta")

    @property
    def backend_path(self):
        return self.build_system.get("backend-path")
