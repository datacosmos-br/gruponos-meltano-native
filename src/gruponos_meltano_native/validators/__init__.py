"""Validadores Meltano Native GrupoNOS.

Este módulo fornece capacidades de validação de dados para sistemas WMS,
seguindo princípios de Clean Architecture e type safety.

Fornece classes e funções para:
    - Validação robusta de dados
    - Conversão de tipos específica Oracle
    - Regras de validação configuráveis
    - Factory functions para diferentes ambientes

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from flext_core import FlextCore

from gruponos_meltano_native.validators.data_validator import (
    DataValidator,
    ValidationError,
    ValidationRule,
    create_validator_for_environment,
)

__all__: FlextCore.Types.StringList = [
    "DataValidator",
    "ValidationError",
    "ValidationRule",
    "create_validator_for_environment",
]
