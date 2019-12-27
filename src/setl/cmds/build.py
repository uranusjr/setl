import argparse
import enum

from setl.projects import Project


class Step(enum.Enum):
    build = "build"
    info = "egg_info"
    clib = "build_clib"
    ext = "build_ext"
    py = "build_py"
    scripts = "build_scripts"


def _handle(project: Project, options) -> int:
    if options.steps is None:
        steps = [Step.egg_info, Step.build]
    else:
        steps = options.steps

    with project.ensure_build_envdir(options.python) as env:
        project.ensure_build_requirements(env)
        project.setuppy(env, *(s.value for s in steps))

    return 0


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("build", description="Build the package")
    parser.set_defaults(steps=None, func=_handle)
    parser.add_argument(
        "--info",
        dest="steps",
        action="append_const",
        const=Step.info,
        help="Build .egg-info directory",
    )
    parser.add_argument(
        "--ext",
        dest="steps",
        action="append_const",
        const=Step.ext,
        help="Build extensions",
    )
    parser.add_argument(
        "--py",
        dest="steps",
        action="append_const",
        const=Step.py,
        help="Build pure Python modules",
    )
    parser.add_argument(
        "--clib",
        dest="steps",
        action="append_const",
        const=Step.clib,
        help="Build C libraries",
    )
    parser.add_argument(
        "--scripts",
        dest="steps",
        action="append_const",
        const=Step.scripts,
        help="Build scripts",
    )
    return parser
