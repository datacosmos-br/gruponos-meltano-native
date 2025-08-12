"""Configuração de DI Meltano Native GrupoNOS - Padronizado FLEXT.

Configuração limpa de injeção de dependência usando apenas padrões FLEXT-core.
SEM código de compatibilidade/legado mantido.

Fornece:
    - Container singleton para injeção de dependências
    - Configuração de dependências core FLEXT
    - Padronização de registro de componentes

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextContainer,
    FlextResult,
    FlextSettings,
    get_flext_container,
    get_logger,
)

logger = get_logger(__name__)


class _ContainerSingleton:
    """Padrão Singleton para container de injeção de dependência.

    Implementa o padrão Singleton para garantir que apenas uma
    instância do container de DI seja criada e reutilizada
    em toda a aplicação.

    Attributes:
        _instance: Instância única do container (privada).

    """

    _instance: FlextContainer | None = None

    @classmethod
    def get_instance(cls) -> FlextContainer:
        """Obtém ou cria a instância do container.

        Método de classe que retorna a instância singleton do container,
        criando-a e configurando dependências se ainda não existir.

        Returns:
            FlextContainer: Instância configurada do container de DI.

        """
        if cls._instance is None:
            cls._instance = get_flext_container()
            _configure_dependencies(cls._instance)
        return cls._instance


def get_gruponos_meltano_container() -> FlextContainer:
    """Obtém container de injeção de dependência Meltano GrupoNOS.

    Função de conveniência que retorna o container de DI configurado
    para uso em toda a aplicação Meltano GrupoNOS.

    Returns:
        FlextContainer: Container de injeção de dependência configurado.

    Example:
        >>> container = get_gruponos_meltano_container()
        >>> resultado = container.resolve("flext_result")
        >>> if resultado.success:
        ...     component = resultado.data

    """
    return _ContainerSingleton.get_instance()


def _configure_dependencies(container: FlextContainer) -> None:
    """Configura dependências core para GrupoNOS Meltano.

    Registra componentes essenciais do FLEXT no container de DI,
    incluindo tipos fundamentais como FlextResult e FlextSettings.

    Args:
        container: Container de injeção de dependência a ser configurado.

    Note:
        Esta função é chamada automaticamente durante a inicialização
        do container e não deve ser chamada diretamente.

    """
    # Register core FLEXT components
    result = container.register("flext_result", FlextResult)
    if not result.success:
        logger.warning("Failed to register FlextResult: %s", result.error)

    settings_result = container.register("flext_settings", FlextSettings)
    if not settings_result.success:
        logger.warning(
            "Failed to register FlextCoreSettings: %s", settings_result.error,
        )
