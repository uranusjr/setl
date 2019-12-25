__all__ = ["Project"]

from .base import BaseProject
from .build import ProjectBuildManagementMixin
from .hook import ProjectPEP517HookCallerMixin
from .meta import ProjectMetadataMixin
from .setup import ProjectSetupMixin


# Order is important here for Mypy; more derived mixins need to come first.
class Project(
    ProjectPEP517HookCallerMixin,
    ProjectBuildManagementMixin,
    ProjectMetadataMixin,
    ProjectSetupMixin,
    BaseProject,
):
    pass
