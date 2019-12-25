import argparse
import enum
import os
import pathlib
import subprocess
import sys

from typing import List

from setl.projects import Project


class Step(enum.Enum):
    sdist = Project.build_sdist
    wheel = Project.build_wheel


def _twine(c: str, targets: List[pathlib.Path]):
    args = [sys.executable, "-m", "twine", c, *(os.fspath(p) for p in targets)]
    subprocess.check_call(args)


def _handle(project, options) -> int:
    steps = options.steps
    if steps is None:
        steps = [Step.sdist, Step.wheel]

    with project.ensure_build_envdir(options.python) as env:
        project.ensure_build_requirements(env)
        targets = [step(project, env) for step in steps]

    if options.check:
        print("Checking distribution integrity...")
        _twine("check", targets)

    _twine("upload", targets)

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
