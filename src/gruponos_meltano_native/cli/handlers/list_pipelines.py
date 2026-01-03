"""List Pipelines Handler - GrupoNOS Meltano Native CLI.

Handler for listing pipelines command operations.
"""

from __future__ import annotations

from flext_core import FlextResult

from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator


class ListPipelinesHandler:
    """Handler for list pipelines command."""

    _orchestrator: GruponosMeltanoOrchestrator

    def __init__(self, orchestrator: GruponosMeltanoOrchestrator) -> None:
        """Initialize the list pipelines handler."""
        self._orchestrator = orchestrator

    def execute(self) -> FlextResult[list[str]]:
        """Execute list pipelines command."""
        jobs = self._orchestrator.list_jobs()
        return FlextResult[list[str]].ok(jobs)
