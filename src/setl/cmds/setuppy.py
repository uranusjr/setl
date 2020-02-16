import argparse

from setl.projects import Project


def _handle(project: Project, options) -> int:
    with project.ensure_build_envdir(options.python) as env:
        proc = project.setuppy(env, *options.arguments, check=False)
    return proc.returncode


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "setup.py",
        description="Run setup.py",
        usage="%(prog)s setup.py [-h] [--] arg [arg ...]",
        epilog=(
            "Use two dashes (`--`) to pass flags (e.g. `--help`) to setup.py. "
            "If you're passing flags both to Setl and setup.py, flags before "
            "`--` go to Setl."
        ),
    )
    parser.set_defaults(steps=None, func=_handle)
    parser.add_argument("arguments", metavar="arg", nargs="+")
    return parser
