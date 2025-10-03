"""Módulo de Monitoramento GrupoNOS.

Este módulo fornece capacidades de monitoramento e alertas para sistemas WMS,
seguindo princípios de Clean Architecture e type safety adequado.

Fornece classes e funções para:
    - Gerenciamento de alertas com múltiplos canais
    - Monitoramento de pipeline e sistema
    - Severidade e tipos de alerta
    - Integração com webhook, email e Slack

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from flext_core import FlextTypes
from gruponos_meltano_native.monitoring.alert_manager import (
    GruponosMeltanoAlert,
    GruponosMeltanoAlertManager,
    GruponosMeltanoAlertService,
    GruponosMeltanoAlertSeverity,
    GruponosMeltanoAlertType,
    create_gruponos_meltano_alert_manager,
)

__all__: FlextTypes.StringList = [
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    "create_gruponos_meltano_alert_manager",
]
