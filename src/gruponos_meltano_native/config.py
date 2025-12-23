"""Configuration module for Gruponos Meltano Native.

Re-exports configuration classes from settings module for backward compatibility.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from gruponos_meltano_native.settings import (
    GruponosMeltanoAlertConfig,
    GruponosMeltanoJobConfig,
    GruponosMeltanoNativeSettings,
    GruponosMeltanoOracleConnectionConfig,
    GruponosMeltanoTargetOracleConfig,
    GruponosMeltanoWMSSourceConfig,
)

# Main config class - alias for settings
GruponosMeltanoNativeConfig = GruponosMeltanoNativeSettings

__all__ = [
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoNativeConfig",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoTargetOracleConfig",
    "GruponosMeltanoWMSSourceConfig",
]
