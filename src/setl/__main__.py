import pathlib
import sys


def main():
    # If we are running from a wheel or without packaging, add the package to
    # sys.path. I stole this technique from pip.
    if not __package__:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
        from setl.cmds import dispatch
    else:
        from .cmds import dispatch

    return dispatch(None)


if __name__ == "__main__":
    sys.exit(main())
