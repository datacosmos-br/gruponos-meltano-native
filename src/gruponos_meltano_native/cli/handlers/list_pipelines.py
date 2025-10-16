"""List Pipelines Handler - GrupoNOS Meltano Native CLI.

Handler for listing pipelines command operations.
"""

from __future__ import annotations

from flext_core import FlextCore

from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator


class ListPipelinesHandler:
    """Handler for list pipelines command."""

    def __init__(self, orchestrator: GruponosMeltanoOrchestrator) -> None:
        """Initialize the list pipelines handler."""
        self._orchestrator = orchestrator

    def execute(self) -> FlextResult[FlextCore.Types.StringList]:
        """Execute list pipelines command."""
        jobs = self._orchestrator.list_jobs()
        return FlextResult[FlextCore.Types.StringList].ok(jobs)
