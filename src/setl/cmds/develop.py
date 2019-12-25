import argparse


def _handle(project, options) -> int:
    with project.ensure_build_envdir(options.python) as env:
        project.ensure_build_requirements(env)
        project.install_for_development()
    return 0


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "develop", description="Install package in 'development mode'"
    )
    parser.set_defaults(steps=None, func=_handle)
    return parser
