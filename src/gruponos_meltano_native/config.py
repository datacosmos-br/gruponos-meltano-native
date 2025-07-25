"""GrupoNOS Meltano Native Configuration - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext-meltano.orchestration.gruponos directly.
"""

from __future__ import annotations

# Import consolidated components from flext-meltano
from flext_meltano.orchestration.gruponos import (
    GruponosMeltanoAlertConfig,
    GruponosMeltanoJobConfig,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoSettings,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
    create_gruponos_meltano_settings,
)

# Re-export for backward compatibility
__all__ = [
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoSettings",
    "GruponosMeltanoTargetOracleConfig",
    "GruponosMeltanoWMSSourceConfig",
    "create_gruponos_meltano_settings",
]
