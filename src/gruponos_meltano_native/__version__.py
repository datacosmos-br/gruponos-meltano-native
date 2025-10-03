"""Version metadata for gruponos meltano native."""

from __future__ import annotations

from importlib.metadata import metadata

_metadata = metadata("gruponos-meltano-native")

__version__ = _metadata["Version"]
__version_info__ = tuple(
    int(part) if part.isdigit() else part for part in __version__.split(".")
)

__all__ = ["__version__", "__version_info__"]
