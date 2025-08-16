"""Infrastructure container tests to increase coverage while using real flext-core.

These tests avoid fallbacks and exercise DI container wiring.
"""
from __future__ import annotations

from flext_core import FlextContainer, FlextResult

from gruponos_meltano_native.infrastructure import (
    get_flext_container,
    get_gruponos_meltano_container,
)


def test_get_flext_container_returns_container() -> None:
    """Test get flext container returns container function."""
    container = get_flext_container()
    assert isinstance(container, FlextContainer)


def test_get_gruponos_meltano_container_registers_core() -> None:
    """Test get gruponos meltano container registers core function."""
    container = get_gruponos_meltano_container()
    # Ensure it is the same singleton instance type
    assert isinstance(container, FlextContainer)

    # Components registered in configuration should be resolvable
    result = container.get("flext_result")
    assert hasattr(result, "success")
    assert result.success
    assert result.data is FlextResult
