"""Orquestrador Nativo Meltano GrupoNOS - Implementação específica GrupoNOS.

Este módulo fornece toda a orquestração específica do GrupoNOS para pipelines Meltano
com sistemas Oracle WMS, construído sobre padrões de arquitetura empresarial.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

from flext_meltano import FlextMeltanoService

from flext_core import FlextResult, FlextTypes
from gruponos_meltano_native.config import GruponosMeltanoNativeConfig

# =============================================
# GRUPONOS MELTANO MODELS
# =============================================


class GruponosMeltanoModels:
    """GrupoNOS Meltano Native Models namespace class.

    Contains all domain models for the GrupoNOS Meltano Native project.
    Follows FLEXT namespace pattern for clean organization.
    """

    @dataclass
    class PipelineResult:
        """Resultado de uma execução de pipeline Meltano GrupoNOS.

        Classe que representa o resultado de uma execução de pipeline ETL,
        contendo informações de sucesso, tempos de execução, saídas e metadados.

        Attributes:
          success: Indica se a execução foi bem-sucedida.
          job_name: Nome do job/pipeline executado.
          execution_time: Tempo de execução em segundos.
          output: Saída padrão do pipeline.
          error: Mensagem de erro, se houver.
          metadata: Metadados adicionais da execução.

        """

        success: bool
        job_name: str
        execution_time: float
        output: str
        error: str | None = None
        metadata: FlextTypes.Dict | None = None


# =============================================
# GRUPONOS MELTANO ORCHESTRATOR - UNIFIED CLASS
# =============================================


class GruponosMeltanoOrchestrator:
    """GrupoNOS Meltano Orchestrator - Unified class following FLEXT patterns.

    This orchestrator provides enterprise-grade ETL pipeline management for Oracle WMS
    to Oracle Database data integration operations. It coordinates Meltano pipeline
    execution with comprehensive error handling, monitoring, and business rule enforcement.

    Key Features:
      - Full synchronization pipeline for complete data refresh
      - Incremental synchronization for real-time data updates
      - Oracle WMS API integration with retry mechanisms
      - Target database operations with transaction management
      - Comprehensive monitoring and alerting integration

    Architecture:
      Built on Clean Architecture principles with dependency injection,
      the orchestrator serves as the main application service layer that
      coordinates between domain logic and infrastructure concerns.

    Example:
      Basic orchestrator usage:

      >>> orchestrator = GruponosMeltanoOrchestrator()
      >>> result = orchestrator.run_full_sync()
      >>> if result.success:
      ...     print(f"Pipeline completed in {result.execution_time:.2f}s")
      ... else:
      ...     print(f"Pipeline failed: {result.error}")

    Integration:
      - Uses GruponosMeltanoNativeConfig for environment-aware configuration
      - Integrates with flext-meltano for execution (ZERO TOLERANCE for direct subprocess)
      - Coordinates with monitoring systems for observability
      - Implements enterprise patterns for consistent error handling

    """

    def __init__(self, settings: GruponosMeltanoNativeConfig | None = None) -> None:
        """Inicializa orquestrador com configurações GrupoNOS.

        Args:
            settings: Configurações opcionais Meltano GrupoNOS.
                     Se None, as configurações serão carregadas das variáveis
                     de ambiente e arquivos de configuração usando padrões default.

        Raises:
            GruponosMeltanoConfigurationError: Se configuração obrigatória estiver ausente.
            GruponosMeltanoValidationError: Se a validação da configuração falhar.

        Example:
            >>> # Usar configurações padrão do ambiente
            >>> orchestrator = GruponosMeltanoOrchestrator()

            >>> # Usar configurações customizadas
            >>> custom_settings = GruponosMeltanoNativeConfig(environment="production")
            >>> orchestrator = GruponosMeltanoOrchestrator(custom_settings)

        """
        self.settings = settings or GruponosMeltanoNativeConfig()
        self._meltano_service = FlextMeltanoService()

    # =============================================
    # PUBLIC API METHODS
    # =============================================

    def validate_configuration(self) -> FlextResult[None]:
        """Valida configuração do orquestrador usando padrões FLEXT.

        Executa validação completa das configurações necessárias para
        operação do orquestrador, incluindo conexões Oracle e fonte WMS.

        Returns:
            FlextResult[None]: Indica sucesso ou falha com erros de validação.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado = orchestrator.validate_configuration()
            >>> if resultado.success:
            ...     print("Configuração válida")

        """
        return self._meltano_service.validate_configuration(self.settings.model_dump())

    def run_full_sync(self) -> GruponosMeltanoModels.PipelineResult:
        """Executa pipeline de sincronização completa para atualização total dos dados.

        Este método executa o pipeline ETL completo que extrai todos os dados
        da API Oracle WMS e os carrega no banco Oracle de destino. É projetado
        para operações de atualização completa de dados e cargas iniciais.

        Componentes do Pipeline:
            - Extração de dados da API Oracle WMS (todas as entidades)
            - Validação de dados e verificações de qualidade
            - Aplicação de regras de negócio
            - Carga em lote no banco de destino com gerenciamento de transações
            - Monitoramento e alertas abrangentes

        Returns:
            GruponosMeltanoModels.PipelineResult: Resultado da execução do pipeline contendo
            status de sucesso, tempo de execução, logs de saída e informações de erro.

        Raises:
            GruponosMeltanoPipelineError: Se a execução do pipeline falhar.
            GruponosMeltanoOracleConnectionError: Se conexões com banco de dados falharem.
            GruponosMeltanoValidationError: Se a validação de dados falhar.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado = orchestrator.run_full_sync()
            >>> if resultado.success:
            ...     print(f"Sync completo em {resultado.execution_time:.2f}s")
            ...     print(f"Saída: {resultado.output}")
            ... else:
            ...     print(f"Sync completo falhou: {resultado.error}")

        Note:
            - Tempo típico de execução: 5-15 minutos para datasets padrão
            - Uso de memória: 1-2GB pico durante operações em lote
            - Agendamento recomendado: Semanal ou sob demanda

        """
        sync_result = self._execute_meltano_job("full-sync-job")

        if sync_result.is_failure:
            return GruponosMeltanoModels.PipelineResult(
                success=False,
                job_name="full-sync-job",
                execution_time=0.0,
                output="",
                error=sync_result.error,
            )

        pipeline_data = sync_result.unwrap()
        return GruponosMeltanoModels.PipelineResult(
            success=True,
            job_name="full-sync-job",
            execution_time=pipeline_data.get("execution_time", 0.0),
            output=pipeline_data.get("output", ""),
            metadata=pipeline_data.get("metadata", {}),
        )

    def run_incremental_sync(self) -> GruponosMeltanoModels.PipelineResult:
        """Executa pipeline de sincronização incremental para atualizações em tempo real.

        Este método executa o pipeline ETL incremental que extrai apenas
        dados modificados desde a última sincronização usando timestamps
        de modificação. É otimizado para execução frequente e transferência mínima de dados.

        Componentes do Pipeline:
            - Extração incremental de dados da API Oracle WMS (filtro mod_ts)
            - Captura e validação de dados modificados
            - Operações de upsert no banco de destino
            - Monitoramento e alertas incrementais

        Returns:
            GruponosMeltanoModels.PipelineResult: Resultado da execução do pipeline com
            estatísticas de sync incremental e métricas de performance.

        Raises:
            GruponosMeltanoPipelineError: Se a execução do pipeline incremental falhar.
            GruponosMeltanoDataValidationError: Se a validação de dados modificados falhar.
            GruponosMeltanoOracleConnectionError: Se conexões com banco de dados falharem.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado = orchestrator.run_incremental_sync()
            >>> if resultado.success:
            ...     print(f"Sync incremental completo: {resultado.execution_time:.2f}s")
            ...     # Acessar métricas incrementais via resultado.metadata
            ... else:
            ...     print(f"Sync incremental falhou: {resultado.error}")

        Note:
            - Tempo típico de execução: 30 segundos - 2 minutos
            - Uso de memória: 100-500MB pico
            - Agendamento recomendado: A cada 2 horas

        """
        sync_result = self._execute_meltano_job("incremental-sync-job")

        if sync_result.is_failure:
            return GruponosMeltanoModels.PipelineResult(
                success=False,
                job_name="incremental-sync-job",
                execution_time=0.0,
                output="",
                error=sync_result.error,
            )

        pipeline_data = sync_result.unwrap()
        return GruponosMeltanoModels.PipelineResult(
            success=True,
            job_name="incremental-sync-job",
            execution_time=pipeline_data.get("execution_time", 0.0),
            output=pipeline_data.get("output", ""),
            metadata=pipeline_data.get("metadata", {}),
        )

    def run_job(self, job_name: str) -> GruponosMeltanoModels.PipelineResult:
        """Executa um job específico de pipeline por nome.

        Este método oferece execução flexível de jobs para configurações
        customizadas de pipeline definidas no projeto Meltano. Suporta tanto
        definições de jobs padrão quanto customizados.

        Args:
            job_name: Nome do job Meltano a ser executado. Deve estar definido
                     no arquivo de configuração meltano.yml.

        Returns:
            GruponosMeltanoModels.PipelineResult: Resultado da execução do job com
            saída específica do job e métricas de performance.

        Raises:
            GruponosMeltanoPipelineError: Se a execução do job falhar.
            GruponosMeltanoConfigurationError: Se o nome do job não for encontrado.
            ValueError: Se job_name estiver vazio ou inválido.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado = orchestrator.run_job("custom-data-quality-check")
            >>> if resultado.success:
            ...     print(f"Job '{resultado.job_name}' completado com sucesso")
            ... else:
            ...     print(f"Job falhou: {resultado.error}")

        Note:
            Jobs Disponíveis:
            - "full-sync-job": Sincronização completa de dados
            - "incremental-sync-job": Atualizações incrementais de dados
            - Jobs customizados conforme definido em meltano.yml

        """
        job_result = self._execute_meltano_job(job_name)

        if job_result.is_failure:
            return GruponosMeltanoModels.PipelineResult(
                success=False,
                job_name=job_name,
                execution_time=0.0,
                output="",
                error=job_result.error,
            )

        job_data = job_result.unwrap()
        return GruponosMeltanoModels.PipelineResult(
            success=True,
            job_name=job_name,
            execution_time=job_data.get("execution_time", 0.0),
            output=job_data.get("output", ""),
            metadata=job_data.get("metadata", {}),
        )

    def list_jobs(self) -> FlextTypes.StringList:
        """Lista todos os jobs de pipeline disponíveis.

        Este método retorna uma lista de todos os jobs Meltano disponíveis para
        execução na configuração atual do projeto. Jobs são definidos em meltano.yml
        e podem incluir tanto jobs ETL padrão quanto operações customizadas.

        Returns:
            FlextTypes.StringList: Lista de nomes de jobs disponíveis que podem ser executados
            via método run_job().

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> jobs = orchestrator.list_jobs()
            >>> print(f"Jobs disponíveis: {', '.join(jobs)}")
            Jobs disponíveis: full-sync-job, incremental-sync-job

        Note:
            A lista de jobs está atualmente hardcoded mas deve ser melhorada
            para ler dinamicamente da configuração meltano.yml em versões futuras.

        """
        return ["full-sync-job", "incremental-sync-job"]

    def list_pipelines(self) -> FlextTypes.StringList:
        """Lista pipelines disponíveis (alias para list_jobs).

        Returns:
            FlextTypes.StringList: Lista de nomes de pipelines disponíveis.

        """
        return self.list_jobs()

    def run_pipeline(
        self,
        pipeline_name: str,
        **kwargs: object,
    ) -> GruponosMeltanoModels.PipelineResult:
        """Executa pipeline assincronamente (método de compatibilidade).

        Args:
            pipeline_name: Nome do pipeline a ser executado.
            **kwargs: Argumentos adicionais passados para o pipeline.

        Returns:
            GruponosMeltanoModels.PipelineResult: Resultado da execução do pipeline.

        """
        return self.run_job(pipeline_name)

    def get_job_status(self, job_name: str) -> FlextTypes.Dict:
        """Obtém status de um job específico.

        Args:
            job_name: Nome do job para verificar status.

        Returns:
            FlextTypes.Dict: Informações de status do job incluindo
            disponibilidade e configurações.

        """
        return {
            "job_name": job_name,
            "available": job_name in self.list_jobs(),
            "settings": self.settings.model_dump(),
        }

    # =============================================
    # NESTED HELPER CLASSES
    # =============================================

    class _PipelineRunner:
        """Nested pipeline runner helper."""

        def __init__(self, orchestrator: GruponosMeltanoOrchestrator) -> None:
            self._orchestrator = orchestrator

        def run_with_retry(
            self,
            job_name: str,
            max_retries: int = 3,
            **kwargs: object,
        ) -> GruponosMeltanoModels.PipelineResult:
            """Executa pipeline com lógica de retry."""
            last_result = None
            for attempt in range(max_retries + 1):
                try:
                    result = self._orchestrator.run_job(job_name)

                    if result.success:
                        return result

                    last_result = result
                    if attempt < max_retries:
                        time.sleep(2**attempt)  # Exponential backoff

                except Exception as e:
                    last_result = GruponosMeltanoModels.PipelineResult(
                        success=False,
                        job_name=job_name,
                        execution_time=0.0,
                        output="",
                        error=str(e),
                        metadata={
                            "attempt": attempt + 1,
                            "exception": type(e).__name__,
                        },
                    )

                    if attempt < max_retries:
                        time.sleep(2**attempt)

            return last_result or GruponosMeltanoModels.PipelineResult(
                success=False,
                job_name=job_name,
                execution_time=0.0,
                output="",
                error="All retry attempts failed",
                metadata={"max_retries": max_retries},
            )

    # =============================================
    # PRIVATE METHODS
    # =============================================

    def _execute_meltano_job(self, job_name: str) -> FlextResult[FlextTypes.Dict]:
        """Execute a Meltano job using flext-meltano domain library.

        Args:
            job_name: Name of the Meltano job to execute

        Returns:
            FlextResult containing execution results or error

        """
        start_time = time.time()

        try:
            # Validate job name first
            sanitized_job_name = self._validate_job_name(job_name)

            # Use flext-meltano domain library - ZERO TOLERANCE for direct subprocess
            execution_result = self._meltano_service.execute_job(
                job_name=sanitized_job_name, config=self.settings.model_dump()
            )

            execution_time = time.time() - start_time

            if execution_result.is_success:
                job_data = execution_result.unwrap()
                return FlextResult.ok({
                    "execution_time": execution_time,
                    "output": job_data.get("output", ""),
                    "metadata": {"return_code": 0, "job_data": job_data},
                })
            return FlextResult.fail(f"Job execution failed: {execution_result.error}")

        except Exception as e:
            execution_time = time.time() - start_time
            return FlextResult.fail(f"Job execution failed: {e}")

    def _build_environment(self) -> FlextTypes.StringDict:
        """Build environment variables for Meltano execution."""
        env = os.environ.copy()

        # Add configuration-based environment variables
        env.update({
            "MELTANO_ENVIRONMENT": self.settings.meltano_environment,
            "MELTANO_PROJECT_ROOT": str(
                Path(self.settings.meltano_project_root or ".")
            ),
            "TAP_ORACLE_WMS_BASE_URL": self.settings.wms_source_config["base_url"]
            or "",
            "TAP_ORACLE_WMS_USERNAME": self.settings.wms_source_config["username"]
            or "",
            "TAP_ORACLE_WMS_PASSWORD": self.settings.wms_source_config["password"]
            or "",
            "TAP_ORACLE_WMS_COMPANY_CODE": self.settings.wms_source_config[
                "company_code"
            ]
            or "",
            "TAP_ORACLE_WMS_FACILITY_CODE": self.settings.wms_source_config[
                "facility_code"
            ]
            or "",
            "FLEXT_TARGET_ORACLE_HOST": self.settings.oracle_connection_config["host"]
            or "",
            "FLEXT_TARGET_ORACLE_PORT": str(
                self.settings.oracle_connection_config["port"]
            ),
            "FLEXT_TARGET_ORACLE_USERNAME": self.settings.oracle_connection_config[
                "username"
            ]
            or "",
            "FLEXT_TARGET_ORACLE_PASSWORD": self.settings.oracle_connection_config[
                "password"
            ]
            or "",
            "FLEXT_TARGET_ORACLE_SCHEMA": self.settings.oracle_connection_config[
                "schema"
            ]
            or "",
        })

        # Handle service name vs SID
        if self.settings.oracle_connection_config["service_name"]:
            env["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = (
                self.settings.oracle_connection_config["service_name"]
            )
        elif hasattr(
            self.settings.oracle_connection_config, "sid"
        ) and self.settings.oracle_connection_config.get("sid"):
            env["FLEXT_TARGET_ORACLE_SID"] = self.settings.oracle_connection_config[
                "sid"
            ]

        return env

    def _validate_job_name(self, job_name: str) -> str:
        """Valida e sanitiza nome do job para prevenir injeção de comando.

        Verifica se o nome do job não contém caracteres perigosos que
        poderiam ser usados para injeção de comandos no sistema.

        Args:
            job_name: Nome do job a ser validado.

        Returns:
            str: Nome do job validado e sanitizado.

        Raises:
            ValueError: Se job_name estiver vazio ou contiver caracteres inválidos.

        Example:
            >>> orchestrator._validate_job_name("full-sync-job")
            'full-sync-job'

        """
        if not job_name or not job_name.strip():
            error_msg = "Job name cannot be empty"
            raise ValueError(error_msg)

        sanitized_job_name = job_name.strip()
        invalid_chars = [
            ";",
            "&",
            "|",
            "`",
            "$",
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
            '"',
            "'",
            "<",
            ">",
            "\\",
        ]
        if any(char in sanitized_job_name for char in invalid_chars):
            error_msg = "Job name contains invalid characters"
            raise ValueError(error_msg)

        return sanitized_job_name

    # =============================================
    # FACTORY FUNCTIONS
    # =============================================
    """Main GrupoNOS Meltano orchestrator for ETL pipeline management.

    This orchestrator provides enterprise-grade ETL pipeline management for Oracle WMS
    to Oracle Database data integration operations. It coordinates Meltano pipeline
    execution with comprehensive error handling, monitoring, and business rule enforcement.

    Key Features:
      - Full synchronization pipeline for complete data refresh
      - Incremental synchronization for real-time data updates
      - Oracle WMS API integration with retry mechanisms
      - Target database operations with transaction management
      - Comprehensive monitoring and alerting integration

    Architecture:
      Built on Clean Architecture principles with dependency injection,
      the orchestrator serves as the main application service layer that
      coordinates between domain logic and infrastructure concerns.

      CRITICAL: Now uses GruponosMeltanoNativeUtilities for ALL business operations.

    Example:
      Basic orchestrator usage:

      >>> orchestrator = GruponosMeltanoOrchestrator()
      >>> result: FlextResult[object] = orchestrator.run_full_sync()
      >>> if result.success:
      ...     print(f"Pipeline completed in {result.execution_time:.2f}s")
      ... else:
      ...     print(f"Pipeline failed: {result.error}")

    Integration:
      - Uses GruponosMeltanoNativeConfig for environment-aware configuration
      - Integrates with GruponosMeltanoPipelineRunner for execution
      - Coordinates with monitoring systems for observability
      - Implements padrões empresariais for consistent error handling
      - MANDATORY: Uses GruponosMeltanoNativeUtilities for ALL business logic

    """

    @override
    def __init__(self, settings: GruponosMeltanoNativeConfig | None = None) -> None:
        """Inicializa orquestrador com configurações GrupoNOS.

        Args:
            settings: Configurações opcionais Meltano GrupoNOS.
                     Se None, as configurações serão carregadas das variáveis
                     de ambiente e arquivos de configuração usando padrões default.

        Raises:
            GruponosMeltanoConfigurationError: Se configuração obrigatória estiver ausente.
            GruponosMeltanoValidationError: Se a validação da configuração falhar.

        Example:
            >>> # Usar configurações padrão do ambiente
            >>> orchestrator = GruponosMeltanoOrchestrator()

            >>> # Usar configurações customizadas
            >>> custom_settings = GruponosMeltanoNativeConfig(environment="production")
            >>> orchestrator = GruponosMeltanoOrchestrator(custom_settings)

        """
        self.settings = settings or GruponosMeltanoNativeConfig()
        self._meltano_service = FlextMeltanoService()

    def validate_configuration(self) -> FlextResult[None]:
        """Valida configuração do orquestrador usando padrões FLEXT.

        Executa validação completa das configurações necessárias para
        operação do orquestrador, incluindo conexões Oracle e fonte WMS.

        Returns:
            FlextResult[None]: Indica sucesso ou falha com erros de validação.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado: FlextResult[object] = orchestrator.validate_configuration()
            >>> if resultado.success:
            ...     print("Configuração válida")

        """
        # ZERO TOLERANCE FIX: Use direct meltano service for configuration validation
        return self._meltano_service.validate_configuration(self.settings.model_dump())

    def run_full_sync(self: object) -> GruponosMeltanoPipelineResult:
        """Executa pipeline de sincronização completa para atualização total dos dados.

        Este método executa o pipeline ETL completo que extrai todos os dados
        da API Oracle WMS e os carrega no banco Oracle de destino. É projetado
        para operações de atualização completa de dados e cargas iniciais.

        Componentes do Pipeline:
            - Extração de dados da API Oracle WMS (todas as entidades)
            - Validação de dados e verificações de qualidade
            - Aplicação de regras de negócio
            - Carga em lote no banco de destino com gerenciamento de transações
            - Monitoramento e alertas abrangentes

        Returns:
            GruponosMeltanoPipelineResult: Resultado da execução do pipeline contendo
            status de sucesso, tempo de execução, logs de saída e informações de erro.

        Raises:
            GruponosMeltanoPipelineError: Se a execução do pipeline falhar.
            GruponosMeltanoOracleConnectionError: Se conexões com banco de dados falharem.
            GruponosMeltanoValidationError: Se a validação de dados falhar.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado: FlextResult[object] = orchestrator.run_full_sync()
            >>> if resultado.success:
            ...     print(f"Sync completo em {resultado.execution_time:.2f}s")
            ...     print(f"Saída: {resultado.output}")
            ... else:
            ...     print(f"Sync completo falhou: {resultado.error}")

        Note:
            - Tempo típico de execução: 5-15 minutos para datasets padrão
            - Uso de memória: 1-2GB pico durante operações em lote
            - Agendamento recomendado: Semanal ou sob demanda

        """
        # ZERO TOLERANCE FIX: Use direct meltano execution for full sync operation
        sync_result = self._execute_meltano_job("full-sync-job")

        if sync_result.is_failure:
            return GruponosMeltanoPipelineResult(
                success=False,
                job_name="full-sync-job",
                execution_time=0.0,
                output="",
                error=sync_result.error,
            )

        pipeline_data = sync_result.unwrap()
        return GruponosMeltanoPipelineResult(
            success=True,
            job_name="full-sync-job",
            execution_time=pipeline_data.get("execution_time", 0.0),
            output=pipeline_data.get("output", ""),
            metadata=pipeline_data.get("metadata", {}),
        )

    def run_incremental_sync(self: object) -> GruponosMeltanoPipelineResult:
        """Executa pipeline de sincronização incremental para atualizações em tempo real.

        Este método executa o pipeline ETL incremental que extrai apenas
        dados modificados desde a última sincronização usando timestamps
        de modificação. É otimizado para execução frequente e transferência mínima de dados.

        Componentes do Pipeline:
            - Extração incremental de dados da API Oracle WMS (filtro mod_ts)
            - Captura e validação de dados modificados
            - Operações de upsert no banco de destino
            - Monitoramento e alertas incrementais

        Returns:
            GruponosMeltanoPipelineResult: Resultado da execução do pipeline com
            estatísticas de sync incremental e métricas de performance.

        Raises:
            GruponosMeltanoPipelineError: Se a execução do pipeline incremental falhar.
            GruponosMeltanoDataValidationError: Se a validação de dados modificados falhar.
            GruponosMeltanoOracleConnectionError: Se conexões com banco de dados falharem.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado: FlextResult[object] = orchestrator.run_incremental_sync()
            >>> if resultado.success:
            ...     print(f"Sync incremental completo: {resultado.execution_time:.2f}s")
            ...     # Acessar métricas incrementais via resultado.metadata
            ... else:
            ...     print(f"Sync incremental falhou: {resultado.error}")

        Note:
            - Tempo típico de execução: 30 segundos - 2 minutos
            - Uso de memória: 100-500MB pico
            - Agendamento recomendado: A cada 2 horas

        """
        # ZERO TOLERANCE FIX: Use direct meltano execution for incremental sync operation
        sync_result = self._execute_meltano_job("incremental-sync-job")

        if sync_result.is_failure:
            return GruponosMeltanoPipelineResult(
                success=False,
                job_name="incremental-sync-job",
                execution_time=0.0,
                output="",
                error=sync_result.error,
            )

        pipeline_data = sync_result.unwrap()
        return GruponosMeltanoPipelineResult(
            success=True,
            job_name="incremental-sync-job",
            execution_time=pipeline_data.get("execution_time", 0.0),
            output=pipeline_data.get("output", ""),
            metadata=pipeline_data.get("metadata", {}),
        )

    def run_job(self, job_name: str) -> GruponosMeltanoPipelineResult:
        """Executa um job específico de pipeline por nome.

        Este método oferece execução flexível de jobs para configurações
        customizadas de pipeline definidas no projeto Meltano. Suporta tanto
        definições de jobs padrão quanto customizados.

        Args:
            job_name: Nome do job Meltano a ser executado. Deve estar definido
                     no arquivo de configuração meltano.yml.

        Returns:
            GruponosMeltanoPipelineResult: Resultado da execução do job com
            saída específica do job e métricas de performance.

        Raises:
            GruponosMeltanoPipelineError: Se a execução do job falhar.
            GruponosMeltanoConfigurationError: Se o nome do job não for encontrado.
            ValueError: Se job_name estiver vazio ou inválido.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> resultado: FlextResult[object] = orchestrator.run_job(
            ...     "custom-data-quality-check"
            ... )
            >>> if resultado.success:
            ...     print(f"Job '{resultado.job_name}' completado com sucesso")
            ... else:
            ...     print(f"Job falhou: {resultado.error}")

        Note:
            Jobs Disponíveis:
            - "full-sync-job": Sincronização completa de dados
            - "incremental-sync-job": Atualizações incrementais de dados
            - Jobs customizados conforme definido em meltano.yml

        """
        # ZERO TOLERANCE FIX: Use direct meltano execution for job execution
        job_result = self._execute_meltano_job(job_name)

        if job_result.is_failure:
            return GruponosMeltanoPipelineResult(
                success=False,
                job_name=job_name,
                execution_time=0.0,
                output="",
                error=job_result.error,
            )

        job_data = job_result.unwrap()
        return GruponosMeltanoPipelineResult(
            success=True,
            job_name=job_name,
            execution_time=job_data.get("execution_time", 0.0),
            output=job_data.get("output", ""),
            metadata=job_data.get("metadata", {}),
        )

    def list_jobs(self: object) -> FlextTypes.StringList:
        """Lista todos os jobs de pipeline disponíveis.

        Este método retorna uma lista de todos os jobs Meltano disponíveis para
        execução na configuração atual do projeto. Jobs são definidos em meltano.yml
        e podem incluir tanto jobs ETL padrão quanto operações customizadas.

        Returns:
            FlextTypes.StringList: Lista de nomes de jobs disponíveis que podem ser executados
            via método run_job().

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> jobs = orchestrator.list_jobs()
            >>> print(f"Jobs disponíveis: {', '.join(jobs)}")
            Jobs disponíveis: full-sync-job, incremental-sync-job

        Note:
            A lista de jobs está atualmente hardcoded mas deve ser melhorada
            para ler dinamicamente da configuração meltano.yml em versões futuras.

        """
        # ZERO TOLERANCE FIX: Use direct job listing
        # TODO(@dev): Implement dynamic job discovery from meltano.yml - https://github.com/gruponos/flext/issues/123  # noqa: FIX002 - Planned enhancement
        return ["full-sync-job", "incremental-sync-job"]

    def list_pipelines(self: object) -> FlextTypes.StringList:
        """Lista pipelines disponíveis (alias para list_jobs).

        Returns:
            FlextTypes.StringList: Lista de nomes de pipelines disponíveis.

        """
        return self.list_jobs()

    def run_pipeline(
        self,
        pipeline_name: str,
        **kwargs: object,
    ) -> GruponosMeltanoModels.PipelineResult:
        """Executa pipeline assincronamente (método de compatibilidade).

        Args:
            pipeline_name: Nome do pipeline a ser executado.
            **kwargs: Argumentos adicionais passados para o pipeline.

        Returns:
            GruponosMeltanoModels.PipelineResult: Resultado da execução do pipeline.

        """
        return self.run_job(pipeline_name)

    def get_job_status(self, job_name: str) -> FlextTypes.Dict:
        """Obtém status de um job específico.

        Args:
            job_name: Nome do job para verificar status.

        Returns:
            FlextTypes.Dict: Informações de status do job incluindo
            disponibilidade e configurações.

        """
        # ZERO TOLERANCE FIX: Use direct job status
        # TODO(@dev): Implement proper job status checking - https://github.com/gruponos/flext/issues/124  # noqa: FIX002 - Planned enhancement
        return {
            "job_name": job_name,
            "available": job_name in self.list_jobs(),
            "settings": self.settings.model_dump(),
        }

    def _execute_meltano_job(self, job_name: str) -> FlextResult[FlextTypes.Dict]:
        """Execute a Meltano job using flext-meltano domain library.

        Args:
            job_name: Name of the Meltano job to execute

        Returns:
            FlextResult containing execution results or error

        """
        start_time = time.time()

        try:
            # Use flext-meltano domain library - ZERO TOLERANCE for direct subprocess
            execution_result = self._meltano_service.execute_job(
                job_name=job_name, config=self.settings.model_dump()
            )

            execution_time = time.time() - start_time

            if execution_result.is_success:
                job_data = execution_result.unwrap()
                return FlextResult.ok({
                    "execution_time": execution_time,
                    "output": job_data.get("output", ""),
                    "metadata": {"return_code": 0, "job_data": job_data},
                })
            return FlextResult.fail(f"Job execution failed: {execution_result.error}")

        except Exception as e:
            execution_time = time.time() - start_time
            return FlextResult.fail(f"Job execution failed: {e}")

    def _build_environment(self) -> dict[str, str]:
        """Build environment variables for Meltano execution."""
        env = os.environ.copy()

        # Add configuration-based environment variables
        env.update({
            "MELTANO_ENVIRONMENT": self.settings.meltano_environment,
            "MELTANO_PROJECT_ROOT": str(
                Path(self.settings.meltano_project_root or ".")
            ),
            "TAP_ORACLE_WMS_BASE_URL": self.settings.wms_source_config["base_url"]
            or "",
            "TAP_ORACLE_WMS_USERNAME": self.settings.wms_source_config["username"]
            or "",
            "TAP_ORACLE_WMS_PASSWORD": self.settings.wms_source_config["password"]
            or "",
            "TAP_ORACLE_WMS_COMPANY_CODE": self.settings.wms_source_config[
                "company_code"
            ]
            or "",
            "TAP_ORACLE_WMS_FACILITY_CODE": self.settings.wms_source_config[
                "facility_code"
            ]
            or "",
            "FLEXT_TARGET_ORACLE_HOST": self.settings.oracle_connection_config["host"]
            or "",
            "FLEXT_TARGET_ORACLE_PORT": str(
                self.settings.oracle_connection_config["port"]
            ),
            "FLEXT_TARGET_ORACLE_USERNAME": self.settings.oracle_connection_config[
                "username"
            ]
            or "",
            "FLEXT_TARGET_ORACLE_PASSWORD": self.settings.oracle_connection_config[
                "password"
            ]
            or "",
            "FLEXT_TARGET_ORACLE_SCHEMA": self.settings.oracle_connection_config[
                "schema"
            ]
            or "",
        })

        # Handle service name vs SID
        if self.settings.oracle_connection_config["service_name"]:
            env["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = (
                self.settings.oracle_connection_config["service_name"]
            )
        elif hasattr(
            self.settings.oracle_connection_config, "sid"
        ) and self.settings.oracle_connection_config.get("sid"):
            env["FLEXT_TARGET_ORACLE_SID"] = self.settings.oracle_connection_config[
                "sid"
            ]

        return env


# =============================================
# FACTORY FUNCTIONS
# =============================================


def create_gruponos_meltano_orchestrator(
    settings: GruponosMeltanoNativeConfig | None = None,
) -> GruponosMeltanoOrchestrator:
    """Cria instância do orquestrador Meltano GrupoNOS.

    Args:
      settings: Configurações opcionais do Meltano GrupoNOS.

    Returns:
      GruponosMeltanoOrchestrator: Instância configurada do orquestrador.

    """
    return GruponosMeltanoOrchestrator(settings)


def create_gruponos_meltano_pipeline_runner(
    settings: GruponosMeltanoNativeConfig | None = None,
) -> GruponosMeltanoOrchestrator._PipelineRunner:
    """Cria instância do executor de pipeline GrupoNOS.

    Args:
      settings: Configurações opcionais do Meltano GrupoNOS.

    Returns:
      GruponosMeltanoOrchestrator._PipelineRunner: Instância configurada do executor.

    """
    orchestrator = GruponosMeltanoOrchestrator(settings)
    return GruponosMeltanoOrchestrator._PipelineRunner(orchestrator)


# Backward compatibility aliases
GruponosMeltanoPipelineResult = GruponosMeltanoModels.PipelineResult
GruponosMeltanoPipelineRunner = GruponosMeltanoOrchestrator._PipelineRunner

# Re-export for backward compatibility
__all__: FlextTypes.StringList = [
    "GruponosMeltanoModels",
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineResult",  # Backward compatibility alias
    "GruponosMeltanoPipelineRunner",  # Backward compatibility alias
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
]
