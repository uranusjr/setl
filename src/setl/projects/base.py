__all__ = ["BaseProject"]

import dataclasses
import pathlib


@dataclasses.dataclass()
class BaseProject:
    root: pathlib.Path
