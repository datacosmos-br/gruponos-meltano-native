"""Módulo de Integração Oracle GrupoNOS.

Este módulo fornece capacidades de integração com banco de dados Oracle
para sistemas WMS, seguindo princípios de Clean Architecture e type safety.

Fornece classes e funções para:
    - Gerenciamento de conexões Oracle
    - Configuração segura de credenciais
    - Teste de conectividade
    - Factory functions para criação de instâncias

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from flext_core import FlextTypes
from gruponos_meltano_native.oracle.connection_manager_enhanced import (
    GruponosMeltanoOracleConnectionManager,
    create_gruponos_meltano_oracle_connection_manager,
)

__all__: FlextTypes.StringList = [
    "GruponosMeltanoOracleConnectionManager",
    "create_gruponos_meltano_oracle_connection_manager",
]
