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

    def run_job(self, job_name: str) -> FlextResult[GruponosMeltanoModels.PipelineResult]:
        """Execute a specific pipeline job by name with railway-oriented error handling.

        Provides flexible job execution for custom pipeline configurations defined
        in the Meltano project. Supports both standard and custom job definitions.

        Args:
            job_name: Name of the Meltano job to execute. Must be defined in meltano.yml.

        Returns:
            FlextResult[PipelineResult]: Railway-oriented result with job execution details
            and performance metrics.

        Example:
            Flexible job execution with proper error handling:

            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> result = orchestrator.run_job("custom-data-quality-check")
            >>> if result.is_success:
            ...     job_result = result.unwrap()
            ...     print(f"✅ Job '{job_result.job_name}' completed successfully")
            ... else:
            ...     logger.error(f"❌ Job failed: {result.error}")

        Note:
            Available Jobs:
            - "full-sync-job": Complete data synchronization
            - "incremental-sync-job": Incremental data updates
            - Custom jobs as defined in meltano.yml

        FLEXT OPTIMIZATION:
        - Uses FlextResult for consistent error handling
        - Validates job name before execution
        - Comprehensive logging and monitoring
        - Structured error reporting

        """
        # Validate job name
        if not job_name or not job_name.strip():
            error_msg = "Job name cannot be empty"
            self._logger.error(error_msg)
            return FlextResult.fail(error_msg)

        sanitized_job_name = job_name.strip()
        self._logger.info(f"Starting job execution: {sanitized_job_name}")

        # Execute job with comprehensive error handling
        execution_result = self._execute_meltano_pipeline(sanitized_job_name)

        if execution_result.is_failure:
            self._logger.error(f"Job execution failed: {execution_result.error}")
            return FlextResult.fail(execution_result.error)

        job_data = execution_result.unwrap()
        job_result = GruponosMeltanoModels.PipelineResult(
            success=True,
            job_name=sanitized_job_name,
            execution_time=job_data.get("execution_time", 0.0),
            output=job_data.get("output", ""),
            metadata=job_data.get("metadata", {}),
        )

        self._logger.info(
            "Job execution completed successfully",
            extra={
                "job_name": sanitized_job_name,
                "execution_time": job_result.execution_time,
                "output_length": len(job_result.output),
            }
        )

        return FlextResult.ok(job_result)

    def list_jobs(self) -> FlextTypes.StringList:
        """List all available pipeline jobs with FLEXT integration.

        Returns a list of all Meltano jobs available for execution in the current
        project configuration. Jobs are defined in meltano.yml and may include
        both standard ETL jobs and custom operations.

        Returns:
            FlextTypes.StringList: List of available job names that can be executed
            via run_job() method.

        Example:
            Listing available jobs with proper error handling:

            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> jobs = orchestrator.list_jobs()
            >>> print(f"📋 Available jobs: {', '.join(jobs)}")
            📋 Available jobs: full-sync-job, incremental-sync-job

        Note:
            Job list is currently hardcoded but should be improved to read
            dynamically from meltano.yml configuration in future versions.

        FLEXT OPTIMIZATION:
        - Uses FlextTypes for type safety
        - Comprehensive documentation with examples
        - Structured logging integration

        """
        available_jobs = ["full-sync-job", "incremental-sync-job"]
        self._logger.debug(f"Available jobs: {available_jobs}")
        return available_jobs

    def list_pipelines(self) -> FlextTypes.StringList:
        """List available pipelines (alias for list_jobs).

        Returns:
            FlextTypes.StringList: List of available pipeline names.

        Note:
            This is an alias for list_jobs() for backward compatibility.

        """
        return self.list_jobs()

    def run_pipeline(
        self,
        pipeline_name: str,
        **kwargs: object,
    ) -> FlextResult[GruponosMeltanoModels.PipelineResult]:
        """Execute pipeline asynchronously (compatibility method).

        Args:
            pipeline_name: Name of the pipeline to execute.
            **kwargs: Additional arguments passed to the pipeline.

        Returns:
            FlextResult[PipelineResult]: Railway-oriented pipeline execution result.

        Note:
            This method provides backward compatibility. Use run_job() for new code.

        """
        return self.run_job(pipeline_name)

    def get_job_status(self, job_name: str) -> FlextResult[FlextTypes.Dict]:
        """Get status of a specific job with comprehensive information.

        Args:
            job_name: Name of the job to check status for.

        Returns:
            FlextResult[Dict]: Railway-oriented result containing job status information
            including availability and configuration details.

        Example:
            Checking job status with error handling:

            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> status_result = orchestrator.get_job_status("full-sync-job")
            >>> if status_result.is_success:
            ...     status = status_result.unwrap()
            ...     print(f"Job available: {status['available']}")
            ... else:
            ...     logger.error(f"Failed to get job status: {status_result.error}")

        FLEXT OPTIMIZATION:
        - Uses FlextResult for consistent error handling
        - Comprehensive status information
        - Type-safe return values

        """
        if not job_name or not job_name.strip():
            return FlextResult.fail("Job name cannot be empty")

        job_status = {
            "job_name": job_name.strip(),
            "available": job_name.strip() in self.list_jobs(),
            "settings": self.settings.model_dump(),
            "environment": self.settings.meltano_environment,
        }

        self._logger.debug(f"Job status retrieved: {job_status}")
        return FlextResult.ok(job_status)

    # =============================================
    # NESTED HELPER CLASSES
    # =============================================

    class _PipelineRunner:
        """Nested pipeline runner helper with retry logic and FLEXT integration.

        Provides advanced pipeline execution capabilities including retry mechanisms,
        exponential backoff, and comprehensive error handling following FLEXT patterns.
        """

        def __init__(self, orchestrator: GruponosMeltanoOrchestrator) -> None:
            """Initialize pipeline runner with orchestrator reference.

            Args:
                orchestrator: The parent orchestrator instance.

            FLEXT OPTIMIZATION:
            - Nested helper class following single-class pattern
            - Reference to parent orchestrator for state management
            - Type-safe initialization
            """
            self._orchestrator = orchestrator
            self._logger = FlextLogger(__name__)

        def run_with_retry(
            self,
            job_name: str,
            max_retries: int = 3,
            **kwargs: object,
        ) -> FlextResult[GruponosMeltanoModels.PipelineResult]:
            """Execute pipeline with comprehensive retry logic and error handling.

            Implements exponential backoff retry mechanism with detailed logging
            and metadata tracking for failed attempts.

            Args:
                job_name: Name of the job to execute with retry.
                max_retries: Maximum number of retry attempts (default: 3).
                **kwargs: Additional arguments passed to the pipeline execution.

            Returns:
                FlextResult[PipelineResult]: Railway-oriented result with retry metadata.

            Example:
                Pipeline execution with retry logic:

                >>> runner = orchestrator._PipelineRunner(orchestrator)
                >>> result = runner.run_with_retry("full-sync-job", max_retries=5)
                >>> if result.is_success:
                ...     print("Pipeline succeeded after retries")
                ... else:
                ...     print(f"All retry attempts failed: {result.error}")

            FLEXT OPTIMIZATION:
            - Uses FlextResult for railway-oriented error handling
            - Exponential backoff with configurable retries
            - Comprehensive logging and metadata tracking
            - Type-safe implementation
            """
            self._logger.info(f"Starting pipeline execution with retry: {job_name}")

            last_result = None
            for attempt in range(max_retries + 1):
                attempt_num = attempt + 1
                self._logger.debug(f"Attempt {attempt_num}/{max_retries + 1} for job: {job_name}")

                try:
                    # Execute job using orchestrator's railway pattern
                    result = self._orchestrator.run_job(job_name)

                    if result.is_success:
                        pipeline_result = result.unwrap()
                        self._logger.info(
                            f"Pipeline succeeded on attempt {attempt_num}",
                            extra={"job_name": job_name, "attempts": attempt_num}
                        )
                        return result

                    # Job failed, prepare for retry
                    last_result = result
                    if attempt < max_retries:
                        backoff_seconds = 2**attempt  # Exponential backoff
                        self._logger.warning(
                            f"Pipeline attempt {attempt_num} failed, retrying in {backoff_seconds}s",
                            extra={"job_name": job_name, "backoff_seconds": backoff_seconds}
                        )
                        time.sleep(backoff_seconds)

                except Exception as e:
                    error_msg = f"Pipeline execution failed on attempt {attempt_num}: {e}"
                    self._logger.error(error_msg, exc_info=True)

                    last_result = FlextResult.fail(error_msg)
                    if attempt < max_retries:
                        backoff_seconds = 2**attempt
                        self._logger.info(f"Retrying after {backoff_seconds}s due to exception")
                        time.sleep(backoff_seconds)

            # All attempts failed
            final_error = f"All {max_retries + 1} retry attempts failed for job: {job_name}"
            self._logger.error(final_error, extra={"job_name": job_name, "max_retries": max_retries})

            return FlextResult.fail(final_error)

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
    # FACTORY METHODS
    # =============================================

    @staticmethod
    def create_orchestrator(
        settings: GruponosMeltanoNativeConfig | None = None,
    ) -> GruponosMeltanoOrchestrator:
        """Cria instância do orquestrador Meltano GrupoNOS.

        Args:
          settings: Configurações opcionais do Meltano GrupoNOS.

        Returns:
          GruponosMeltanoOrchestrator: Instância configurada do orquestrador.

        """
        return GruponosMeltanoOrchestrator(settings)

    @staticmethod
    def create_pipeline_runner(
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


# =============================================
# BACKWARD COMPATIBILITY FUNCTIONS
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
    return GruponosMeltanoOrchestrator.create_orchestrator(settings)


def create_gruponos_meltano_pipeline_runner(
    settings: GruponosMeltanoNativeConfig | None = None,
) -> GruponosMeltanoOrchestrator._PipelineRunner:
    """Cria instância do executor de pipeline GrupoNOS.

    Args:
      settings: Configurações opcionais do Meltano GrupoNOS.

    Returns:
      GruponosMeltanoOrchestrator._PipelineRunner: Instância configurada do executor.

    """
    return GruponosMeltanoOrchestrator.create_pipeline_runner(settings)


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
