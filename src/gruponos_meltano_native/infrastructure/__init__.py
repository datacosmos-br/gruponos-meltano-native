"""Camada de infraestrutura para Meltano Native GrupoNOS - Padronizado FLEXT.

Este módulo fornece componentes de infraestrutura padrão FLEXT seguindo
princípios de Clean Architecture e Domain-Driven Design.

Fornece:
    - Container de injeção de dependência
    - Configurações de infraestrutura FLEXT
    - Padrões de registro de componentes
    - Integração com flext-core

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextSettings,
    FlextContainer,
    get_flext_container,
)

from gruponos_meltano_native.infrastructure.di_container import (
    get_gruponos_meltano_container,
)

# FLEXT Standard Infrastructure Exports - NO legacy functions
__all__: list[str] = [
    # FLEXT Core Infrastructure
    "FlextSettings",
    "FlextContainer",
    "get_flext_container",
    # GrupoNOS Meltano Infrastructure
    "get_gruponos_meltano_container",
]
