"""Validadores Meltano Native GrupoNOS - Validação padronizada FLEXT.

Este módulo fornece capacidades de validação de dados seguindo padrões
FLEXT e princípios de Clean Architecture.

Fornece classes e funções para:
    - Validação robusta de dados
    - Conversão de tipos específica Oracle
    - Regras de validação configuráveis
    - Factory functions para diferentes ambientes

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib

# FLEXT Standard Validation Components
with contextlib.suppress(ImportError):
    from gruponos_meltano_native.validators.data_validator import (
        DataValidator as _DataValidator,
        create_validator_for_environment as _create_validator_for_environment,
    )

    # FLEXT Standard Validation Classes
    class GruponosMeltanoDataValidator(_DataValidator):
        """Validador de dados Meltano GrupoNOS seguindo padrões FLEXT.

        Estende o validador base com funcionalidades específicas
        do GrupoNOS para integração Oracle WMS.
        """

    # FLEXT Standard Factory Function
    def create_gruponos_meltano_validator_for_environment(
        environment: str = "dev",
        **_kwargs: object,
    ) -> GruponosMeltanoDataValidator:
        """Cria validador de dados Meltano GrupoNOS para ambiente.

        Função factory que cria um validador configurado adequadamente
        para o ambiente especificado (desenvolvimento vs produção).

        Args:
            environment: Ambiente de destino (dev, prod, etc.).
            **_kwargs: Parâmetros de configuração adicionais.

        Returns:
            GruponosMeltanoDataValidator: Instância configurada do validador.

        Example:
            >>> validator = create_gruponos_meltano_validator_for_environment("prod")
            >>> erros = validator.validate(dados)

        """
        base_validator = _create_validator_for_environment(environment)
        # DataValidator doesn't have config - pass the constructor args
        return GruponosMeltanoDataValidator(
            rules=getattr(base_validator, "rules", None),
            strict_mode=getattr(base_validator, "strict_mode", False),
        )

    # Backward compatibility aliases
    DataValidator = GruponosMeltanoDataValidator  # Legacy alias
    create_validator_for_environment = (
        create_gruponos_meltano_validator_for_environment  # Legacy alias
    )

# FLEXT Standard Validation Exports
__all__: list[str] = [
    # Legacy Compatibility (deprecated)
    "DataValidator",
    # FLEXT Standard Classes
    "GruponosMeltanoDataValidator",
    # FLEXT Standard Factory Functions
    "create_gruponos_meltano_validator_for_environment",
    "create_validator_for_environment",
]
