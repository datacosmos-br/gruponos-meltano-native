"""Health Check Handler - GrupoNOS Meltano Native CLI.

Handler for health check command operations.
"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextCore


class HealthHandler:
    """Handler for health check command."""

    @staticmethod
    def execute() -> FlextCore.Result[FlextCore.Types.StringDict]:
        """Execute health check."""
        return FlextCore.Result[FlextCore.Types.StringDict].ok({
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
        })
