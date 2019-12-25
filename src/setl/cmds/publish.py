import argparse
import enum
import os
import subprocess
import sys

from setl.projects import Project


class Step(enum.Enum):
    sdist = Project.build_sdist
    wheel = Project.build_wheel


def _handle(project, options) -> int:
    steps = options.steps
    if steps is None:
        steps = [Step.sdist, Step.wheel]

    with project.ensure_build_envdir(options.python) as env:
        project.ensure_build_requirements(env)
        targets = [os.fspath(step(project, env)) for step in steps]

    cmd = [sys.executable, "-m", "twine"]

    if options.check:
        subprocess.check_call(cmd + ["check", *targets])

    subprocess.check_call(cmd + ["upload", *targets])

    return 0


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "publish", description="Publish distributions to PyPI"
    )
    parser.set_defaults(steps=None, func=_handle)
    parser.add_argument(
        "--no-check",
        dest="check",
        action="store_false",
        default=True,
        help="Do not check the distributions before upload",
    )
    parser.add_argument(
        "--source",
        dest="steps",
        action="append_const",
        const=Step.sdist,
        help="Publish the sdist",
    )
    parser.add_argument(
        "--wheel",
        dest="steps",
        action="append_const",
        const=Step.wheel,
        help="Publish the wheel",
    )
    return parser
