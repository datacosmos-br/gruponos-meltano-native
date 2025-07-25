"""GrupoNOS Meltano Native Exceptions - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext_meltano.exceptions directly.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import consolidated components from flext-meltano
from flext_meltano.exceptions import (
    GruponosMeltanoAlertDeliveryError,
    GruponosMeltanoAlertError,
    GruponosMeltanoConfigurationError,
    GruponosMeltanoDataError,
    GruponosMeltanoDataQualityError,
    GruponosMeltanoDataValidationError,
    GruponosMeltanoError,
    GruponosMeltanoMissingConfigError,
    GruponosMeltanoMonitoringError,
    GruponosMeltanoOracleConnectionError,
    GruponosMeltanoOracleError,
    GruponosMeltanoOracleQueryError,
    GruponosMeltanoOracleTimeoutError,
    GruponosMeltanoOrchestrationError,
    GruponosMeltanoPipelineError,
    GruponosMeltanoPipelineTimeoutError,
    GruponosMeltanoPipelineValidationError,
    GruponosMeltanoSingerError,
    GruponosMeltanoTapError,
    GruponosMeltanoTargetError,
    GruponosMeltanoValidationError,
)

# Re-export for backward compatibility
__all__ = [
    "GruponosMeltanoAlertDeliveryError",
    "GruponosMeltanoAlertError",
    "GruponosMeltanoConfigurationError",
    "GruponosMeltanoDataError",
    "GruponosMeltanoDataQualityError",
    "GruponosMeltanoDataValidationError",
    "GruponosMeltanoError",
    "GruponosMeltanoMissingConfigError",
    "GruponosMeltanoMonitoringError",
    "GruponosMeltanoOracleConnectionError",
    "GruponosMeltanoOracleError",
    "GruponosMeltanoOracleQueryError",
    "GruponosMeltanoOracleTimeoutError",
    "GruponosMeltanoOrchestrationError",
    "GruponosMeltanoPipelineError",
    "GruponosMeltanoPipelineTimeoutError",
    "GruponosMeltanoPipelineValidationError",
    "GruponosMeltanoSingerError",
    "GruponosMeltanoTapError",
    "GruponosMeltanoTargetError",
    "GruponosMeltanoValidationError",
]
