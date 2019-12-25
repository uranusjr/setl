import argparse


def _handle(project, options) -> int:
    with project.ensure_build_envdir(options.python) as _:
        project.clean()


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "clean", description="Clean up temporary files from build"
    )
    parser.set_defaults(steps=None, func=_handle)
    return parser
