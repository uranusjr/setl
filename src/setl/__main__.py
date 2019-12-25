def main():
    from .cmds import dispatch

    return dispatch(None)


if __name__ == "__main__":
    import sys

    sys.exit(main())
