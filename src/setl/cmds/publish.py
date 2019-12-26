import argparse
import enum

from setl.projects import Project

from ._utils import twine


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

    if options.check:
        twine("check", *targets)

    if options.repository:
        upload_flags = ["--repository", options.repository]
    elif options.repository_url:
        upload_flags = ["--repository-url", options.repository_url]
    else:
        upload_flags = []
    twine("upload", *upload_flags, *targets)

    return 0


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "publish", description="Publish distributions to PyPI"
    )
    parser.set_defaults(steps=None, func=_handle)
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
    parser.add_argument(
        "--no-check",
        dest="check",
        action="store_false",
        default=True,
        help="Do not check the distributions before upload",
    )

    repo_group = parser.add_mutually_exclusive_group()
    repo_group.add_argument(
        "--repository",
        metavar="NAME",
        default=None,
        help="Repository declared in the config file to upload to",
    )
    repo_group.add_argument(
        "--repository-url",
        metavar="URL",
        default=None,
        help="Repository URL to upload to",
    )

    return parser
