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

from flext_core import FlextTypes

# Import validator classes and functions from dedicated module
from gruponos_meltano_native.validators.validator_classes import (
    DataValidator,
    GruponosMeltanoDataValidator,
    create_gruponos_meltano_validator_for_environment,
    create_validator_for_environment,
)

# Exportações de Validação Padrão Empresarial
__all__: FlextTypes.Core.StringList = [
    # Legacy Compatibility (deprecated)
    "DataValidator",
    # Classes Padrão Empresarial
    "GruponosMeltanoDataValidator",
    # Funções Factory Padrão Empresarial
    "create_gruponos_meltano_validator_for_environment",
    "create_validator_for_environment",
]
