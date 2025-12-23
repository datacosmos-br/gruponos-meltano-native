"""CLI module for Gruponos Meltano Native.

Re-exports the main CLI class and instance from the _cli_main module.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""
# ruff: noqa: PLC2701

from __future__ import annotations

from gruponos_meltano_native._cli_main import (
    GruponosMeltanoNativeCli,
    cli,
)

__all__ = [
    "GruponosMeltanoNativeCli",
    "cli",
]
