import argparse
import enum

from setl.projects import Project


class Step(enum.Enum):
    sdist = Project.build_sdist
    wheel = Project.build_wheel


def _handle(project: Project, options) -> int:
    steps = options.steps
    if steps is None:
        steps = [Step.sdist, Step.wheel]

    with project.ensure_build_envdir(options.python) as env:
        project.ensure_build_requirements(env)
        targets = [step(project, env) for step in steps]

    print("Created distributions:")
    for t in targets:
        print(f"  - {t.name}")

    return 0


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("dist", description="Create distributions")
    parser.set_defaults(steps=None, func=_handle)
    parser.add_argument(
        "--source",
        dest="steps",
        action="append_const",
        const=Step.sdist,
        help="Create a source distribution",
    )
    parser.add_argument(
        "--wheel",
        dest="steps",
        action="append_const",
        const=Step.wheel,
        help="Create a wheel",
    )
    return parser
