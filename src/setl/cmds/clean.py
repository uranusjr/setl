import argparse

from setl.projects import Project


def _handle(project: Project, options) -> int:
    with project.ensure_build_envdir(options.python) as env:
        project.clean(env)
    return 0


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "clean", description="Clean up temporary files from build"
    )
    parser.set_defaults(steps=None, func=_handle)
    return parser
