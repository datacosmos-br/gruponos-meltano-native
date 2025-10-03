"""GrupoNOS Meltano Native Protocols - Type protocols for the project.

Provides type protocols and interfaces for GrupoNOS Meltano Native components.
Uses flext-core protocol patterns for consistency.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from typing import Protocol

from flext_core import FlextProtocols


class GruponosMeltanoNativeProtocols(FlextProtocols):
    """GrupoNOS Meltano Native Protocols namespace class.

    Contains protocol definitions for the GrupoNOS Meltano Native project.
    Extends FlextProtocols for consistency with FLEXT ecosystem.
    """

    class ConfigValidator(Protocol):
        """Protocol for configuration validation."""

        def validate(self) -> bool:
            """Validate configuration."""
            ...

    class PipelineRunner(Protocol):
        """Protocol for pipeline execution."""

        def run_pipeline(self, pipeline_name: str) -> bool:
            """Run a pipeline by name."""
            ...

    class AlertHandler(Protocol):
        """Protocol for alert handling."""

        def send_alert(self, message: str, severity: str) -> None:
            """Send an alert with given message and severity."""
            ...

    class DataValidator(Protocol):
        """Protocol for data validation."""

        def validate_data(self, data: dict) -> list[str]:
            """Validate data and return list of errors."""
            ...


# Export protocols namespace
__all__ = ["GruponosMeltanoNativeProtocols"]