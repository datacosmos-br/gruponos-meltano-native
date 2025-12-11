"""Run Pipeline Handler - GrupoNOS Meltano Native CLI.

Handler for pipeline run command operations.
"""

from __future__ import annotations

from flext_core import FlextResult

from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator


class RunHandler:
    """Handler for pipeline run command."""

    def __init__(self, orchestrator: GruponosMeltanoOrchestrator) -> None:
        """Initialize the run handler."""
        self._orchestrator = orchestrator

    def execute(
        self,
        pipeline_name: str,
        *,
        dry_run: bool = False,
        force: bool = False,
    ) -> FlextResult[dict[str, str | bool]]:
        """Execute pipeline run command."""
        if dry_run:
            validation_result = self._orchestrator.validate_configuration()
            if validation_result.is_failure:
                return FlextResult[dict[str, str | bool]].fail(
                    f"Pipeline validation failed: {validation_result.error}"
                )

            return FlextResult[dict[str, str | bool]].ok({
                "pipeline": pipeline_name,
                "status": "validated",
                "dry_run": True,
                "force": force,
            })

        execution_result = self._orchestrator.run_job(pipeline_name)

        if execution_result.is_failure:
            return FlextResult[dict[str, str | bool]].fail(
                f"Pipeline execution failed: {execution_result.error}"
            )

        pipeline_result = execution_result.value
        return FlextResult[dict[str, str | bool]].ok({
            "pipeline": pipeline_name,
            "status": "completed",
            "execution_time": pipeline_result.execution_time,
            "dry_run": dry_run,
            "force": force,
        })
