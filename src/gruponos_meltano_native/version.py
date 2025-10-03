"""Project metadata for gruponos meltano native."""

from __future__ import annotations

from importlib.metadata import metadata
from typing import Final

_metadata = metadata("gruponos-meltano-native")

__version__ = _metadata["Version"]
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in __version__.split(".")
)


class GruponosMeltanoNativeVersion:
    """Simple version class for gruponos meltano native."""

    def __init__(self, version: str, version_info: tuple[int | str, ...]) -> None:
        """Initialize version."""
        self.version = version
        self.version_info = version_info


VERSION: Final[GruponosMeltanoNativeVersion] = GruponosMeltanoNativeVersion(
    __version__, __version_info__
)

__all__ = ["VERSION", "GruponosMeltanoNativeVersion", "__version__", "__version_info__"]
