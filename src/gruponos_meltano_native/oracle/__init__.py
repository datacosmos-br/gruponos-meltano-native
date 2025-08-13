"""Módulo de Integração Oracle - Padronizado FLEXT.

Este módulo fornece capacidades de integração com banco de dados Oracle
seguindo padrões FLEXT, princípios de Clean Architecture e type safety adequado.

Fornece classes e funções para:
    - Gerenciamento de conexões Oracle
    - Configuração segura de credenciais
    - Teste de conectividade
    - Factory functions para criação de instâncias

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    GruponosMeltanoOracleConnectionManager,
    create_gruponos_meltano_oracle_connection_manager,
)

# Public API exports - FLEXT standard only
__all__: list[str] = [
    # FLEXT Standard Classes
    "GruponosMeltanoOracleConnectionManager",
    # Factory Functions
    "create_gruponos_meltano_oracle_connection_manager",
]
