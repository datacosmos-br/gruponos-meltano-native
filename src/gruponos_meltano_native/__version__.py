"""Version metadata for gruponos meltano native."""

from __future__ import annotations

from flext_core.metadata import build_metadata_exports

_metadata = build_metadata_exports(__file__)

__version__: Final[str] = cast("str", _metadata["__version__"])
__version_info__: Final[tuple[int | str, ...]] = cast(
    "tuple[int | str, ...]",
    _metadata["__version_info__"],
)

__all__ = ["__version__", "__version_info__"]
from typing import Final
