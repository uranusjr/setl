import argparse
import subprocess
import pathlib


class _ProjectNotFound(Exception):
    pass


def _find_project_root() -> pathlib.Path:
    for path in pathlib.Path.cwd().joinpath("setup.py").parents:
        if path.joinpath("setup.py").is_file():
            return path
    raise _ProjectNotFound()


def _handle(options) -> int:
    command = [options.python, "setup.py"]
    if options.steps is None:
        command.append("build")
    else:
        command.extend(options.steps)

    # TODO: Install PEP 518 build requirements.

    subprocess.call(
        command, cwd=_find_project_root(), check=True,
    )


def get_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("build", description="Build the package")
    parser.set_defaults(steps=None, func=_handle)
    parser.add_argument(
        "--ext",
        dest="steps",
        action="append_const",
        const="build_ext",
        help="Build extensions",
    )
    parser.add_argument(
        "--py",
        dest="steps",
        action="append_const",
        const="build_py",
        help="Build pure Python modules",
    )
    parser.add_argument(
        "--clib",
        dest="steps",
        action="append_const",
        const="build_clib",
        help="Build C libraries",
    )
    parser.add_argument(
        "--scripts",
        dest="steps",
        action="append_const",
        const="build_scripts",
        help="Build scripts",
    )
    return parser
