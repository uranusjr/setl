"""Packaging tool for PEP 518 projects with Setuptools as the backend.
"""

__version__ = "0.1.0"


def main():
    import sys
    from .cmds import dispatch

    sys.exit(dispatch(None))
