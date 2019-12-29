import enum


class Error(enum.IntEnum):
    # Error code 1 is reserved because Python returns it on an uncaught
    # exception. We want to be more specific if we return on our own.
    unknown = 1
    project_not_found = 2
