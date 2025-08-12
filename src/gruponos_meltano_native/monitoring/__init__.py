"""Módulo de Monitoramento - Padronizado FLEXT.

Este módulo fornece capacidades de monitoramento e alertas seguindo padrões FLEXT,
princípios de Clean Architecture e type safety adequado.

Fornece classes e funções para:
    - Gerenciamento de alertas com múltiplos canais
    - Monitoramento de pipeline e sistema
    - Severidade e tipos de alerta
    - Integração com webhook, email e Slack

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Direct imports - NO wrappers or legacy aliases
from gruponos_meltano_native.monitoring.alert_manager import (
    GruponosMeltanoAlert,
    GruponosMeltanoAlertManager,
    GruponosMeltanoAlertService,
    GruponosMeltanoAlertSeverity,
    GruponosMeltanoAlertType,
    create_gruponos_meltano_alert_manager,
)

# Public API exports - FLEXT standard only
__all__: list[str] = [
    # FLEXT Standard Classes
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    # Factory Functions
    "create_gruponos_meltano_alert_manager",
]
