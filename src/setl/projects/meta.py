__all__ = ["ProjectMetadataMixin"]

from typing import Any, Dict, List, Optional

import cached_property
import toml

from .base import BaseProject


_DEFAULT_BUILD_REQUIREMENTS = ["setuptools", "wheel"]
_DEFAULT_BUILD_BACKEND = "setuptools.build_meta:__legacy__"
_DEFAULT_BUILD_SYSTEM = {
    "requires": _DEFAULT_BUILD_REQUIREMENTS,
    "build-backend": _DEFAULT_BUILD_BACKEND,
}


class ProjectMetadataMixin(BaseProject):
    @cached_property.cached_property
    def _build_system(self) -> Dict[str, Any]:
        with self.root.joinpath("pyproject.toml").open() as f:
            data = toml.load(f)
        try:
            build_system = data["build-system"]
        except KeyError:
            return _DEFAULT_BUILD_SYSTEM
        if "build-backend" not in build_system:
            return _DEFAULT_BUILD_SYSTEM
        return build_system

    @property
    def build_requirements(self) -> List[str]:
        return self._build_system.get("requires", _DEFAULT_BUILD_REQUIREMENTS)

    @property
    def build_backend(self) -> str:
        return self._build_system.get("build-backend", _DEFAULT_BUILD_BACKEND)

    @property
    def backend_path(self) -> Optional[str]:
        return self._build_system.get("backend-path")
