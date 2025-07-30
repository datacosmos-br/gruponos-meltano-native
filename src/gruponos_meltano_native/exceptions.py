"""GrupoNOS Meltano Native Exceptions.

All GrupoNOS-specific exceptions extending FLEXT core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextConfigurationError,
    FlextError,
    FlextOperationError,
    FlextProcessingError,
    FlextValidationError,
)


# GrupoNOS-specific errors - base hierarchy
class GruponosMeltanoError(FlextError):
    """Base GrupoNOS Meltano error."""

    def __init__(
        self, message: str = "GrupoNOS Meltano error", **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS Meltano error with context."""
        super().__init__(message, error_code="GRUPONOS_MELTANO_ERROR", context=kwargs)


class GruponosMeltanoConfigurationError(FlextConfigurationError):
    """GrupoNOS configuration error."""

    def __init__(
        self,
        message: str = "GrupoNOS configuration error",
        config_key: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS configuration error with context."""
        context = kwargs.copy()
        if config_key is not None:
            context["config_key"] = config_key

        super().__init__(f"GrupoNOS config: {message}", **context)


class GruponosMeltanoOrchestrationError(FlextOperationError):
    """GrupoNOS orchestration error."""

    def __init__(
        self,
        message: str = "GrupoNOS orchestration failed",
        operation: str | None = None,
        stage: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS orchestration error with context."""
        super().__init__(
            f"GrupoNOS orchestration: {message}",
            operation=operation,
            stage=stage,
            context=kwargs,
        )


class GruponosMeltanoPipelineError(FlextProcessingError):
    """GrupoNOS pipeline error."""

    def __init__(
        self,
        message: str = "GrupoNOS pipeline failed",
        pipeline_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS pipeline error with context."""
        context = kwargs.copy()
        if pipeline_name is not None:
            context["pipeline_name"] = pipeline_name

        super().__init__(f"GrupoNOS pipeline: {message}", **context)


class GruponosMeltanoValidationError(FlextValidationError):
    """GrupoNOS validation error."""

    def __init__(
        self,
        message: str = "GrupoNOS validation failed",
        field: str | None = None,
        value: object = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS validation error with context."""
        validation_details = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = value

        super().__init__(
            f"GrupoNOS validation: {message}",
            validation_details=validation_details,
            context=kwargs,
        )


class GruponosMeltanoAlertError(GruponosMeltanoError):
    """Alert system error."""

    def __init__(
        self,
        message: str = "GrupoNOS alert error",
        alert_type: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS alert error with context."""
        context = kwargs.copy()
        if alert_type is not None:
            context["alert_type"] = alert_type

        super().__init__(f"GrupoNOS alert: {message}", **context)


class GruponosMeltanoAlertDeliveryError(GruponosMeltanoAlertError):
    """Alert delivery error."""

    def __init__(
        self,
        message: str = "GrupoNOS alert delivery failed",
        delivery_channel: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS alert delivery error with context."""
        context = kwargs.copy()
        if delivery_channel is not None:
            context["delivery_channel"] = delivery_channel

        super().__init__(f"Alert delivery: {message}", **context)


class GruponosMeltanoDataError(FlextProcessingError):
    """Data processing error."""

    def __init__(
        self,
        message: str = "GrupoNOS data processing failed",
        data_source: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize GrupoNOS data error with context."""
        context = kwargs.copy()
        if data_source is not None:
            context["data_source"] = data_source

        super().__init__(f"GrupoNOS data: {message}", **context)


class GruponosMeltanoDataQualityError(GruponosMeltanoDataError):
    """Data quality error."""


class GruponosMeltanoDataValidationError(GruponosMeltanoDataError):
    """Data validation error."""


class GruponosMeltanoMissingConfigError(GruponosMeltanoConfigurationError):
    """Missing configuration error."""


class GruponosMeltanoMonitoringError(GruponosMeltanoError):
    """Monitoring system error."""


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
