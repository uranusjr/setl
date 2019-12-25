import argparse
import enum


class Step(enum.Enum):
    build = "build"
    clib = "build_clib"
    ext = "build_ext"
    py = "build_py"
    scripts = "build_scripts"


def _handle(project, options) -> int:
    steps = options.steps
    if steps is None:
        steps = [Step.build]

    with project.ensure_build_envdir(options.python) as env:
        project.ensure_build_requirements(env)
        project.build(s.value for s in steps)

    return 0


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("build", description="Build the package")
    parser.set_defaults(steps=None, func=_handle)
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
