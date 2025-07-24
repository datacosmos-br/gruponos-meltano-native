"""🚨 ARCHITECTURAL COMPLIANCE: ELIMINATED DUPLICATE DIContainer.

REFATORADO COMPLETO:
- REMOVIDA TODAS as duplicações de DIContainer (576 linhas!)
- USA APENAS a implementação oficial do flext-core
- Mantém apenas utilitários GrupoNOS-específicos

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# 🚨 ARCHITECTURAL COMPLIANCE: Use ONLY official flext-core DIContainer - NO duplications
from flext_core.config.base import DIContainer

# ==================== GRUPONOS-SPECIFIC DI UTILITIES ====================

_gruponos_container_instance: DIContainer | None = None


def get_gruponos_container() -> DIContainer:
    """Get GrupoNOS-specific DI container instance."""
    global _gruponos_container_instance
    if _gruponos_container_instance is None:
        _gruponos_container_instance = DIContainer()
    return _gruponos_container_instance


def configure_gruponos_dependencies() -> None:
    """Configure GrupoNOS dependencies using official DIContainer."""
    container = get_gruponos_container()

    # Import GrupoNOS-specific services
    try:
        from gruponos_meltano_native.config import get_gruponos_settings

        settings = get_gruponos_settings()

        # Register settings
        container.register(type(settings), settings)

        # Configure any dependencies if settings support it
        if hasattr(settings, "configure_dependencies"):
            settings.configure_dependencies(container)
    except ImportError:
        # GrupoNOS configuration not available
        pass
