import pathlib
import sys


def main():
    # If we are running from a wheel or without packaging, add the package to
    # sys.path. I stole this technique from pip.
    if not __package__:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
        argv = sys.argv[1:]
        from setl.cmds import dispatch
    else:
        argv = sys.argv
        from .cmds import dispatch

    return dispatch(argv)


if __name__ == "__main__":
    sys.exit(main())
