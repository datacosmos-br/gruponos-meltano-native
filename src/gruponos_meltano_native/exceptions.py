"""GrupoNOS Meltano Native Exceptions following flext-core patterns.

All GrupoNOS-specific exceptions extending FLEXT core abstractions using
proper static inheritance. Follows the architectural principle of keeping
generic functionality in abstract libraries (flext-core) and using them
correctly in concrete projects.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)


# Define GrupoNOS-specific exception hierarchy using static inheritance
class GruponosMeltanoError(FlextError):
    """Base GrupoNOS Meltano error following flext-core patterns."""

    def __init__(self, message: str = "GrupoNOS Meltano error", **kwargs: object) -> None:
        """Initialize GrupoNOS Meltano error with context."""
        super().__init__(
            message,
            error_code="GRUPONOS_MELTANO_ERROR",
            context=kwargs,
        )


class GruponosMeltanoValidationError(FlextValidationError):
    """GrupoNOS validation errors following flext-core patterns."""

    def __init__(self, message: str = "GrupoNOS validation error", **kwargs: object) -> None:
        """Initialize GrupoNOS validation error."""
        super().__init__(
            message,
            error_code="GRUPONOS_MELTANO_VALIDATION_ERROR",
            context=kwargs,
        )


class GruponosMeltanoConfigurationError(FlextConfigurationError):
    """GrupoNOS configuration errors following flext-core patterns."""

    def __init__(self, message: str = "GrupoNOS configuration error", **kwargs: object) -> None:
        """Initialize GrupoNOS configuration error."""
        super().__init__(
            message,
            **kwargs,
        )


class GruponosMeltanoConnectionError(FlextConnectionError):
    """GrupoNOS connection errors following flext-core patterns."""

    def __init__(self, message: str = "GrupoNOS connection error", **kwargs: object) -> None:
        """Initialize GrupoNOS connection error."""
        super().__init__(
            message,
            **kwargs,
        )


class GruponosMeltanoProcessingError(FlextProcessingError):
    """GrupoNOS processing errors following flext-core patterns."""

    def __init__(self, message: str = "GrupoNOS processing error", **kwargs: object) -> None:
        """Initialize GrupoNOS processing error."""
        super().__init__(
            message,
            **kwargs,
        )


class GruponosMeltanoAuthenticationError(FlextAuthenticationError):
    """GrupoNOS authentication errors following flext-core patterns."""

    def __init__(self, message: str = "GrupoNOS authentication error", **kwargs: object) -> None:
        """Initialize GrupoNOS authentication error."""
        super().__init__(
            message,
            **kwargs,
        )


class GruponosMeltanoTimeoutError(FlextTimeoutError):
    """GrupoNOS timeout errors following flext-core patterns."""

    def __init__(self, message: str = "GrupoNOS timeout error", **kwargs: object) -> None:
        """Initialize GrupoNOS timeout error."""
        super().__init__(
            message,
            **kwargs,
        )


# Specialized domain-specific errors extending base classes
class GruponosMeltanoOrchestrationError(GruponosMeltanoError):
    """GrupoNOS orchestration error."""

    def __init__(
        self,
        message: str = "GrupoNOS orchestration failed",
        operation: str | None = None,
        stage: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS orchestration error with context."""
        if operation is not None:
            kwargs["operation"] = operation
        if stage is not None:
            kwargs["stage"] = stage
        super().__init__(f"GrupoNOS orchestration: {message}", **kwargs)


class GruponosMeltanoPipelineError(GruponosMeltanoOrchestrationError):
    """GrupoNOS pipeline error extending orchestration error."""

    def __init__(
        self,
        message: str = "GrupoNOS pipeline failed",
        pipeline_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS pipeline error with context."""
        # Extract pipeline_type if provided, otherwise use None
        pipeline_type = kwargs.pop("pipeline_type", None)
        if pipeline_name is not None:
            kwargs["pipeline_name"] = pipeline_name
        # Extract operation and stage for parent class, keep other kwargs
        operation_obj = kwargs.pop("operation", None)
        stage_obj = kwargs.pop("stage", None)
        operation = str(operation_obj) if operation_obj is not None else None
        stage = str(stage_obj) if stage_obj is not None else None
        if pipeline_type is not None:
            kwargs["pipeline_type"] = pipeline_type
        super().__init__(
            message=f"GrupoNOS pipeline: {message}",
            operation=operation,
            stage=stage,
            **kwargs,
        )


# Monitoring error hierarchy
class GruponosMeltanoMonitoringError(GruponosMeltanoError):
    """Monitoring system error."""


# Domain-specific error classes extending foundation hierarchy
class GruponosMeltanoAlertError(GruponosMeltanoMonitoringError):
    """Alert system error."""


class GruponosMeltanoAlertDeliveryError(GruponosMeltanoAlertError):
    """Alert delivery error."""


class GruponosMeltanoDataError(GruponosMeltanoError):
    """Data processing error."""


class GruponosMeltanoDataQualityError(GruponosMeltanoDataError):
    """Data quality error."""


class GruponosMeltanoDataValidationError(GruponosMeltanoDataError):
    """Data validation error."""


class GruponosMeltanoMissingConfigError(GruponosMeltanoError):
    """Missing configuration error."""


class GruponosMeltanoOracleError(GruponosMeltanoError):
    """Oracle database error."""


class GruponosMeltanoOracleConnectionError(GruponosMeltanoOracleError):
    """Oracle connection error."""


class GruponosMeltanoOracleQueryError(GruponosMeltanoOracleError):
    """Oracle query error."""


class GruponosMeltanoOracleTimeoutError(GruponosMeltanoOracleError):
    """Oracle timeout error."""


class GruponosMeltanoPipelineTimeoutError(GruponosMeltanoPipelineError):
    """Pipeline timeout error."""


class GruponosMeltanoPipelineValidationError(GruponosMeltanoPipelineError):
    """Pipeline validation error."""


class GruponosMeltanoSingerError(GruponosMeltanoError):
    """Singer protocol error."""


class GruponosMeltanoTapError(GruponosMeltanoSingerError):
    """Tap execution error."""


class GruponosMeltanoTargetError(GruponosMeltanoSingerError):
    """Target execution error."""


__all__: list[str] = [
    "GruponosMeltanoAlertDeliveryError",
    "GruponosMeltanoAlertError",
    "GruponosMeltanoAuthenticationError",
    "GruponosMeltanoConfigurationError",
    "GruponosMeltanoConnectionError",
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
    "GruponosMeltanoProcessingError",
    "GruponosMeltanoSingerError",
    "GruponosMeltanoTapError",
    "GruponosMeltanoTargetError",
    "GruponosMeltanoTimeoutError",
    "GruponosMeltanoValidationError",
]
