__all__ = ["InterpreterNotFound", "Project", "PyUnavailable"]

from ._envs import PyUnavailable
from .base import BaseProject
from .build import InterpreterNotFound, ProjectBuildManagementMixin
from .clean import ProjectCleanMixin
from .dev import ProjectDevelopMixin
from .hook import ProjectPEP517HookCallerMixin
from .meta import ProjectMetadataMixin
from .setup import ProjectSetupMixin


# Order is important here for Mypy; more derived mixins need to come first.
class Project(
    ProjectCleanMixin,
    ProjectDevelopMixin,
    ProjectPEP517HookCallerMixin,
    ProjectBuildManagementMixin,
    ProjectMetadataMixin,
    ProjectSetupMixin,
    BaseProject,
):
    pass
