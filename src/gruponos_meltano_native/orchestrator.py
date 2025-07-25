"""GrupoNOS Meltano Native Orchestrator - consolidated in flext-meltano.

This module is now a compatibility layer that imports from flext-meltano.
All new development should use flext-meltano.orchestration.gruponos directly.
"""

from __future__ import annotations

# Import consolidated components from flext-meltano
from flext_meltano.orchestration.gruponos import (
    GruponosMeltanoOrchestrator,
    GruponosMeltanoPipelineResult,
    GruponosMeltanoPipelineRunner,
    create_gruponos_meltano_orchestrator,
    create_gruponos_meltano_pipeline_runner,
)

# Re-export for backward compatibility
__all__ = [
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineResult",
    "GruponosMeltanoPipelineRunner",
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
]
