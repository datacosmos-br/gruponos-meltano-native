"""Monitoring Module - FLEXT standardized.

This module provides monitoring and alerting capabilities following FLEXT standards,
Clean Architecture principles, and proper type safety.

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
__all__ = [
    # FLEXT Standard Classes
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    # Factory Functions
    "create_gruponos_meltano_alert_manager",
]
