"""Health Check Handler - GrupoNOS Meltano Native CLI.

Handler for health check command operations.
"""

from __future__ import annotations

from datetime import UTC, datetime


class HealthHandler:
    """Handler for health check command."""

    @staticmethod
    def execute() -> FlextResult[dict[str, str]]:
        """Execute health check."""
        return FlextResult[dict[str, str]].ok({
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
        })
