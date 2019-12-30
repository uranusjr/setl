import enum


class Error(enum.IntEnum):
    # Error code 1 is reserved because Python returns it on an uncaught
    # exception. We want to be more specific if we return on our own.
    unknown = 0x01
    project_not_found = 0x02

    # Errors resolving interpreter from `--python`.
    interpreter_not_found = 0x10
    py_unavailable = 0x11
