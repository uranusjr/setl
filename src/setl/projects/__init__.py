__all__ = ["Project"]

from .base import BaseProject
from .build import ProjectBuildManagementMixin
from .meta import ProjectMetadataMixin
from .setup import ProjectSetupMixin


class Project(
    ProjectBuildManagementMixin,
    ProjectMetadataMixin,
    ProjectSetupMixin,
    BaseProject,
):
    pass
