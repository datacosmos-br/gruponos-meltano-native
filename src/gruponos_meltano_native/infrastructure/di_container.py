"""GrupoNOS Meltano Native DI Configuration - FLEXT standardized.

Clean dependency injection configuration using only FLEXT-core standards.
NO legacy/backward compatibility code maintained.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextBaseSettings,
    FlextContainer,
    FlextResult,
    get_flext_container,
    get_logger,
)

logger = get_logger(__name__)

_container_instance: FlextContainer | None = None


def get_gruponos_meltano_container() -> FlextContainer:
    """Get GrupoNOS Meltano dependency injection container."""
    global _container_instance
    if _container_instance is None:
        _container_instance = get_flext_container()
        _configure_dependencies(_container_instance)
    return _container_instance


def _configure_dependencies(container: FlextContainer) -> None:
    """Configure core dependencies for GrupoNOS Meltano."""
    # Register core FLEXT components
    result = container.register("flext_result", FlextResult)
    if not result.success:
        logger.warning(f"Failed to register FlextResult: {result.error}")

    settings_result = container.register("flext_settings", FlextBaseSettings)
    if not settings_result.success:
        logger.warning(f"Failed to register FlextCoreSettings: {settings_result.error}")
