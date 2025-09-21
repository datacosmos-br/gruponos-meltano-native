"""Exceções Nativas Meltano GrupoNOS.

Todas as exceções específicas do GrupoNOS para integração Oracle WMS,
seguindo padrões arquiteturais estabelecidos e princípios de design limpo.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from flext_core import FlextExceptions, FlextTypes


# Definir hierarquia de exceções específica do GrupoNOS usando herança estática
class GruponosMeltanoError(FlextExceptions.Error):
    """Erro base Meltano GrupoNOS seguindo padrões flext-core.

    Classe base para todas as exceções específicas do sistema
    Meltano GrupoNOS, estendendo FlextExceptions.Error para manter
    consistência arquitetural.
    """

    def __init__(
        self,
        message: str = "GrupoNOS Meltano error",
        *,
        error_code: str | None = None,
        context: FlextTypes.Core.Dict | None = None,
    ) -> None:
        """Inicializa erro Meltano GrupoNOS com contexto.

        Args:
            message: Mensagem de erro descritiva.
            error_code: Código de erro específico; padrão GENERIC_ERROR.
            context: Contexto adicional do erro (detalhes estruturados).

        """
        # Ensure default code matches test expectation (GENERIC_ERROR)
        # Call FlextExceptions.Error directly to avoid MRO conflicts with ConfigurationError
        FlextExceptions.Error.__init__(
            self,
            message=message,
            error_code=error_code or "GENERIC_ERROR",
            context=context or {},
        )


class GruponosMeltanoConfigurationError(
    GruponosMeltanoError,
    FlextExceptions._ConfigurationError,
):
    """Erros de configuração GrupoNOS seguindo padrões flext-core.

    Exceção lançada quando há problemas na configuração
    do sistema, como parâmetros ausentes ou inválidos.
    """

    def __init__(
        self,
        message: str = "GrupoNOS configuration error",
        *,
        error_code: str | None = None,
        context: FlextTypes.Core.Dict | None = None,
    ) -> None:
        """Inicializa erro de configuração GrupoNOS.

        Args:
            message: Mensagem descrevendo o problema de configuração.
            error_code: Código de erro opcional.
            context: Contexto adicional do erro.

        """
        # Call GruponosMeltanoError to set generic error code and context, avoid
        # passing error_code twice into FlextExceptions.ConfigurationError chain.
        GruponosMeltanoError.__init__(
            self,
            message=message,
            error_code=error_code,
            context=context,
        )


# Definir após ConfigurationError para suportar herança desejada no teste
class GruponosMeltanoValidationError(
    GruponosMeltanoConfigurationError,
    FlextExceptions._ValidationError,
):
    """Erros de validação GrupoNOS seguindo padrões flext-core.

    Exceção lançada quando dados ou configurações não passam
    nas validações do sistema GrupoNOS.
    """

    def __init__(
        self,
        message: str = "GrupoNOS validation error",
        *,
        error_code: str | None = None,
        context: FlextTypes.Core.Dict | None = None,
        field: str | None = None,
        value: object = None,
        validation_details: object = None,
    ) -> None:
        """Inicializa erro de validação GrupoNOS.

        Args:
            message: Mensagem descrevendo o erro de validação.
            error_code: Código de erro opcional.
            context: Contexto adicional do erro.
            field: Campo que falhou na validação.
            value: Valor que falhou na validação.
            validation_details: Detalhes da validação.

        """
        # Call _ValidationError directly to handle validation-specific context
        FlextExceptions.ValidationError.__init__(
            self,
            message=message,
            field=field,
            value=value,
            validation_details=validation_details,
            context=context or {},
            error_code=error_code,
        )


class GruponosMeltanoConnectionError(FlextExceptions._ConnectionError):
    """Erros de conexão GrupoNOS seguindo padrões flext-core.

    Exceção lançada quando há falhas de conectividade
    com sistemas externos como bancos de dados ou APIs.
    """

    def __init__(self, message: str = "GrupoNOS connection error") -> None:
        """Inicializa erro de conexão GrupoNOS.

        Args:
            message: Mensagem descrevendo o problema de conexão.

        """
        super().__init__(message)


class GruponosMeltanoProcessingError(FlextExceptions._ProcessingError):
    """Erros de processamento GrupoNOS seguindo padrões flext-core.

    Exceção lançada durante o processamento de dados,
    incluindo transformações e operações ETL.
    """

    def __init__(self, message: str = "GrupoNOS processing error") -> None:
        """Inicializa erro de processamento GrupoNOS.

        Args:
            message: Mensagem descrevendo o erro de processamento.

        """
        super().__init__(message)


class GruponosMeltanoAuthenticationError(FlextExceptions._AuthenticationError):
    """Erros de autenticação GrupoNOS seguindo padrões flext-core.

    Exceção lançada quando há falhas na autenticação
    com sistemas externos ou credenciais inválidas.
    """

    def __init__(self, message: str = "GrupoNOS authentication error") -> None:
        """Inicializa erro de autenticação GrupoNOS.

        Args:
            message: Mensagem descrevendo o problema de autenticação.

        """
        super().__init__(message)


class GruponosMeltanoTimeoutError(FlextExceptions._TimeoutError):
    """Erros de timeout GrupoNOS seguindo padrões flext-core.

    Exceção lançada quando operações excedem
    o tempo limite estabelecido.
    """

    def __init__(self, message: str = "GrupoNOS timeout error") -> None:
        """Inicializa erro de timeout GrupoNOS.

        Args:
            message: Mensagem descrevendo o problema de timeout.

        """
        super().__init__(message)


# Specialized domain-specific errors extending base classes
class GruponosMeltanoOrchestrationError(GruponosMeltanoError):
    """Erro de orquestração GrupoNOS.

    Exceção lançada quando há falhas na orquestração
    de pipelines ETL ou coordenação de componentes.
    """

    def __init__(
        self,
        message: str = "GrupoNOS orchestration failed",
    ) -> None:
        """Inicializa erro de orquestração GrupoNOS.

        Args:
            message: Mensagem descrevendo a falha de orquestração.

        """
        super().__init__(f"GrupoNOS orchestration: {message}")


class GruponosMeltanoPipelineError(GruponosMeltanoOrchestrationError):
    """Erro de pipeline GrupoNOS estendendo erro de orquestração.

    Exceção lançada quando há falhas específicas
    na execução de pipelines individuais.
    """

    def __init__(
        self,
        message: str = "GrupoNOS pipeline failed",
    ) -> None:
        """Inicializa erro de pipeline GrupoNOS.

        Args:
            message: Mensagem descrevendo a falha do pipeline.

        """
        super().__init__(f"GrupoNOS pipeline: {message}")


# Monitoring error hierarchy
class GruponosMeltanoMonitoringError(GruponosMeltanoError):
    """Erro do sistema de monitoramento.

    Exceção base para erros relacionados ao sistema
    de monitoramento e observabilidade.
    """


# Domain-specific error classes extending foundation hierarchy
class GruponosMeltanoAlertError(GruponosMeltanoMonitoringError):
    """Erro do sistema de alertas.

    Exceção lançada quando há problemas no
    sistema de alertas e notificações.
    """


class GruponosMeltanoAlertDeliveryError(GruponosMeltanoAlertError):
    """Erro de entrega de alerta.

    Exceção lançada quando falha a entrega de alertas
    via email, webhook ou outros canais.
    """


class GruponosMeltanoDataError(GruponosMeltanoError):
    """Erro de processamento de dados.

    Exceção base para erros relacionados ao
    processamento e manipulação de dados.
    """


class GruponosMeltanoDataQualityError(GruponosMeltanoDataError):
    """Erro de qualidade de dados.

    Exceção lançada quando dados não atendem
    aos critérios de qualidade estabelecidos.
    """


class GruponosMeltanoDataValidationError(GruponosMeltanoDataError):
    """Erro de validação de dados.

    Exceção lançada quando dados falham
    nas validações de formato ou integridade.
    """


class GruponosMeltanoMissingConfigError(GruponosMeltanoError):
    """Erro de configuração ausente.

    Exceção lançada quando configurações
    obrigatórias não são encontradas.
    """


class GruponosMeltanoOracleError(GruponosMeltanoError):
    """Erro de banco de dados Oracle.

    Exceção base para todos os erros relacionados
    a operações com banco de dados Oracle.
    """


class GruponosMeltanoOracleConnectionError(GruponosMeltanoOracleError):
    """Erro de conexão Oracle.

    Exceção lançada quando há falhas na
    conexão com o banco de dados Oracle.
    """


class GruponosMeltanoOracleQueryError(GruponosMeltanoOracleError):
    """Erro de consulta Oracle.

    Exceção lançada quando há falhas na
    execução de consultas SQL no Oracle.
    """


class GruponosMeltanoOracleTimeoutError(GruponosMeltanoOracleError):
    """Erro de timeout Oracle.

    Exceção lançada quando operações Oracle
    excedem o tempo limite configurado.
    """


class GruponosMeltanoPipelineTimeoutError(GruponosMeltanoPipelineError):
    """Erro de timeout de pipeline.

    Exceção lançada quando a execução de pipeline
    excede o tempo limite estabelecido.
    """


class GruponosMeltanoPipelineValidationError(GruponosMeltanoPipelineError):
    """Erro de validação de pipeline.

    Exceção lançada quando a configuração ou
    estrutura do pipeline é inválida.
    """


class GruponosMeltanoSingerError(GruponosMeltanoError):
    """Erro de protocolo Singer.

    Exceção base para erros relacionados ao
    protocolo Singer e seus componentes.
    """


class GruponosMeltanoTapError(GruponosMeltanoSingerError):
    """Erro de execução de tap.

    Exceção lançada quando há falhas na
    execução de taps Singer.
    """


class GruponosMeltanoTargetError(GruponosMeltanoSingerError):
    """Erro de execução de target.

    Exceção lançada quando há falhas na
    execução de targets Singer.
    """


__all__: FlextTypes.Core.StringList = [
    "GruponosMeltanoAlertDeliveryError",
    "GruponosMeltanoAlertError",
    "GruponosMeltanoAuthenticationError",
    "GruponosMeltanoConfigurationError",
    "GruponosMeltanoConnectionError",
    "GruponosMeltanoDataError",
    "GruponosMeltanoDataQualityError",
    "GruponosMeltanoDataValidationError",
    "GruponosMeltanoError",
    "GruponosMeltanoMissingConfigError",
    "GruponosMeltanoMonitoringError",
    "GruponosMeltanoOracleConnectionError",
    "GruponosMeltanoOracleError",
    "GruponosMeltanoOracleQueryError",
    "GruponosMeltanoOracleTimeoutError",
    "GruponosMeltanoOrchestrationError",
    "GruponosMeltanoPipelineError",
    "GruponosMeltanoPipelineTimeoutError",
    "GruponosMeltanoPipelineValidationError",
    "GruponosMeltanoProcessingError",
    "GruponosMeltanoSingerError",
    "GruponosMeltanoTapError",
    "GruponosMeltanoTargetError",
    "GruponosMeltanoTimeoutError",
    "GruponosMeltanoValidationError",
]
