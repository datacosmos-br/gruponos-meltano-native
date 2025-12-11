"""Run With Retry Handler - GrupoNOS Meltano Native CLI.

Handler for run with retry command operations.
"""

from __future__ import annotations

import time

from flext_core import FlextResult

from gruponos_meltano_native.orchestrator import GruponosMeltanoOrchestrator


class RunWithRetryHandler:
    """Handler for run with retry command."""

    def __init__(self, orchestrator: GruponosMeltanoOrchestrator) -> None:
        """Initialize the run with retry handler."""
        self._orchestrator = orchestrator

    def execute(
        self,
        pipeline_name: str,
        max_retries: int = 3,
        *,
        retry_delay: int = 5,
    ) -> FlextResult[dict[str, str | int]]:
        """Execute run with retry command."""
        attempts_used = 0

        for attempt in range(max_retries + 1):
            attempts_used = attempt + 1
            execution_result = self._orchestrator.run_job(pipeline_name)

            if execution_result.is_success:
                pipeline_result = execution_result.value
                return FlextResult[dict[str, str | int]].ok({
                    "pipeline": pipeline_name,
                    "retries": max_retries,
                    "retry_delay": retry_delay,
                    "attempts_used": attempts_used,
                    "status": "completed",
                    "execution_time": pipeline_result.execution_time,
                })

            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                return FlextResult[dict[str, str | int]].fail(
                    f"Pipeline execution failed after {attempts_used} attempts: {execution_result.error}"
                )

        # This should not be reached, but just in case
        return FlextResult[dict[str, str | int]].fail("Unexpected error in retry logic")
