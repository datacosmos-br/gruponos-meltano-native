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


class _ContainerSingleton:
    """Singleton pattern for dependency injection container."""

    _instance: FlextContainer | None = None

    @classmethod
    def get_instance(cls) -> FlextContainer:
        """Get or create the container instance."""
        if cls._instance is None:
            cls._instance = get_flext_container()
            _configure_dependencies(cls._instance)
        return cls._instance


def get_gruponos_meltano_container() -> FlextContainer:
    """Get GrupoNOS Meltano dependency injection container."""
    return _ContainerSingleton.get_instance()


def _configure_dependencies(container: FlextContainer) -> None:
    """Configure core dependencies for GrupoNOS Meltano."""
    # Register core FLEXT components
    result = container.register("flext_result", FlextResult)
    if not result.success:
        logger.warning("Failed to register FlextResult: %s", result.error)

    settings_result = container.register("flext_settings", FlextBaseSettings)
    if not settings_result.success:
        logger.warning("Failed to register FlextCoreSettings: %s", settings_result.error)
