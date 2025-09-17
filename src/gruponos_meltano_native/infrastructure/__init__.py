"""Camada de infraestrutura para Meltano Native GrupoNOS.

Este módulo fornece componentes de infraestrutura para integração Oracle WMS,
seguindo princípios de Clean Architecture e Domain-Driven Design.

Fornece:
    - Container de injeção de dependência
    - Configurações de infraestrutura
    - Padrões de registro de componentes
    - Integração com bibliotecas base

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from flext_core import (
    FlextConfig,
    FlextContainer,
    FlextTypes,
)
from gruponos_meltano_native.infrastructure.di_container import (
    get_gruponos_meltano_container,
)

# Exportações de Infraestrutura Padrão Empresarial - NO legacy functions
__all__: FlextTypes.Core.StringList = [
    # FLEXT Core Infrastructure
    "FlextConfig",
    "FlextContainer",
    # GrupoNOS Meltano Infrastructure
    "get_gruponos_meltano_container",
]
