"""Health Check Handler - GrupoNOS Meltano Native CLI.

Handler for health check command operations.
"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextResult, FlextTypes


class HealthHandler:
    """Handler for health check command."""

    @staticmethod
    def execute() -> FlextResult[FlextTypes.StringDict]:
        """Execute health check."""
        return FlextResult[FlextTypes.StringDict].ok({
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
        })