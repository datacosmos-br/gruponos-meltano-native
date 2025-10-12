"""Orquestrador Nativo Meltano GrupoNOS - Implementação específica GrupoNOS.

Este módulo fornece toda a orquestração específica do GrupoNOS para pipelines Meltano
com sistemas Oracle WMS, construído sobre padrões de arquitetura empresarial.

Refactored to use modular architecture with separated concerns:
- Pipeline models in models/pipeline.py
- Pipeline execution in core/pipeline_executor.py
- Orchestration logic focused on high-level coordination

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from flext_core import FlextLogger, FlextResult, FlextService

from gruponos_meltano_native.config import GruponosMeltanoNativeConfig
from gruponos_meltano_native.core.pipeline_executor import MeltanoPipelineExecutor
from gruponos_meltano_native.models.pipeline import (
    PipelineConfiguration,
    PipelineResult,
    PipelineStatus,
)

# Import for backward compatibility
GruponosMeltanoModels = type('GruponosMeltanoModels', (), {
    'PipelineResult': PipelineResult,
})

# =============================================
# GRUPONOS MELTANO PIPELINE RESULT
# =============================================

class GruponosMeltanoPipelineResult:
    """Classe que representa o resultado de uma execução de pipeline ETL,
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


class GruponosMeltanoOrchestrator(FlextService[GruponosMeltanoNativeConfig]):
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
        super().__init__()
        self.settings = settings or GruponosMeltanoNativeConfig()
        self.logger = FlextLogger(__name__)
        self._meltano_service = FlextMeltanoService()

        # Validate initial configuration during initialization
        validation_result = self._validate_initial_configuration()
        if validation_result.is_failure:
            error_msg = (
                f"Initial configuration validation failed: {validation_result.error}"
            )
            self.logger.error(error_msg)
            init_error_msg = (
                f"Orchestrator initialization failed: {validation_result.error}"
            )
            raise ValueError(init_error_msg)

        self.logger.debug("GruponosMeltanoOrchestrator initialized successfully")

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

    def run_full_sync(self) -> FlextResult[GruponosMeltanoModels.PipelineResult]:
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
            FlextResult[GruponosMeltanoModels.PipelineResult]: Railway-oriented result with
            pipeline execution details and comprehensive error handling.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> result = orchestrator.run_full_sync()
            >>> if result.is_success:
            ...     pipeline_result = result.unwrap()
            ...     print(f"Sync completo em {pipeline_result.execution_time:.2f}s")
            ...     print(f"Saída: {pipeline_result.output}")
            ... else:
            ...     print(f"Sync completo falhou: {result.error}")

        Note:
            - Tempo típico de execução: 5-15 minutos para datasets padrão
            - Uso de memória: 1-2GB pico durante operações em lote
            - Agendamento recomendado: Semanal ou sob demanda

        FLEXT OPTIMIZATION:
        - Uses FlextResult for railway-oriented error handling
        - Comprehensive error reporting without exceptions
        - Type-safe result processing

        """
        sync_result = self._execute_meltano_pipeline("full-sync-job")

        if sync_result.is_failure:
            return FlextResult.fail(sync_result.error)

        pipeline_data = sync_result.unwrap()
        pipeline_result = GruponosMeltanoModels.PipelineResult(
            success=True,
            job_name="full-sync-job",
            execution_time=pipeline_data.get("execution_time", 0.0),
            output=pipeline_data.get("output", ""),
            metadata=pipeline_data.get("metadata", {}),
        )

        return FlextResult.ok(pipeline_result)

    def run_incremental_sync(self) -> FlextResult[GruponosMeltanoModels.PipelineResult]:
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
            FlextResult[GruponosMeltanoModels.PipelineResult]: Railway-oriented result with
            incremental sync execution details and comprehensive error handling.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator()
            >>> result = orchestrator.run_incremental_sync()
            >>> if result.is_success:
            ...     pipeline_result = result.unwrap()
            ...     print(
            ...         f"Sync incremental completo: {pipeline_result.execution_time:.2f}s"
            ...     )
            ...     # Acessar métricas incrementais via pipeline_result.metadata
            ... else:
            ...     print(f"Sync incremental falhou: {result.error}")

        Note:
            - Tempo típico de execução: 30 segundos - 2 minutos
            - Uso de memória: 100-500MB pico
            - Agendamento recomendado: A cada 2 horas

        FLEXT OPTIMIZATION:
        - Uses FlextResult for railway-oriented error handling
        - Comprehensive error reporting without exceptions
        - Type-safe result processing

        """
        sync_result = self._execute_meltano_pipeline("incremental-sync-job")

        if sync_result.is_failure:
            return FlextResult.fail(sync_result.error)

        pipeline_data = sync_result.unwrap()
        pipeline_result = GruponosMeltanoModels.PipelineResult(
            success=True,
            job_name="incremental-sync-job",
            execution_time=pipeline_data.get("execution_time", 0.0),
            output=pipeline_data.get("output", ""),
            metadata=pipeline_data.get("metadata", {}),
        )

        return FlextResult.ok(pipeline_result)

    def run_job(
        self, job_name: str
    ) -> FlextResult[GruponosMeltanoModels.PipelineResult]:
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
            self.logger.error(error_msg)
            return FlextResult.fail(error_msg)

        sanitized_job_name = job_name.strip()
        self.logger.info(f"Starting job execution: {sanitized_job_name}")

        # Execute job with comprehensive error handling
        execution_result = self._execute_meltano_pipeline(sanitized_job_name)

        if execution_result.is_failure:
            self.logger.error(f"Job execution failed: {execution_result.error}")
            return FlextResult.fail(execution_result.error)

        job_data = execution_result.unwrap()
        job_result = GruponosMeltanoModels.PipelineResult(
            success=True,
            job_name=sanitized_job_name,
            execution_time=job_data.get("execution_time", 0.0),
            output=job_data.get("output", ""),
            metadata=job_data.get("metadata", {}),
        )

        self.logger.info(
            "Job execution completed successfully",
            extra={
                "job_name": sanitized_job_name,
                "execution_time": job_result.execution_time,
                "output_length": len(job_result.output),
            },
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
        self.logger.debug(f"Available jobs: {available_jobs}")
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
    ) -> FlextResult[GruponosMeltanoModels.PipelineResult]:
        """Execute pipeline asynchronously (compatibility method).

        Args:
            pipeline_name: Name of the pipeline to execute.

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

        self.logger.debug(f"Job status retrieved: {job_status}")
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
            self.logger = FlextLogger(__name__)

        def run_with_retry(
            self,
            job_name: str,
            max_retries: int = 3,
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
            self.logger.info(f"Starting pipeline execution with retry: {job_name}")

            for attempt in range(max_retries + 1):
                attempt_num = attempt + 1
                self.logger.debug(
                    f"Attempt {attempt_num}/{max_retries + 1} for job: {job_name}"
                )

                try:
                    # Execute job using orchestrator's railway pattern
                    result = self._orchestrator.run_job(job_name)

                    if result.is_success:
                        self.logger.info(
                            f"Pipeline succeeded on attempt {attempt_num}",
                            extra={"job_name": job_name, "attempts": attempt_num},
                        )
                        return result

                    # Job failed, prepare for retry
                    if attempt < max_retries:
                        backoff_seconds = 2**attempt  # Exponential backoff
                        self.logger.warning(
                            f"Pipeline attempt {attempt_num} failed, retrying in {backoff_seconds}s",
                            extra={
                                "job_name": job_name,
                                "backoff_seconds": backoff_seconds,
                            },
                        )
                        time.sleep(backoff_seconds)

                except Exception as e:
                    error_msg = (
                        f"Pipeline execution failed on attempt {attempt_num}: {e}"
                    )
                    self.logger.exception(error_msg)

                    if attempt < max_retries:
                        backoff_seconds = 2**attempt
                        self.logger.info(
                            f"Retrying after {backoff_seconds}s due to exception"
                        )
                        time.sleep(backoff_seconds)

            # All attempts failed
            final_error = (
                f"All {max_retries + 1} retry attempts failed for job: {job_name}"
            )
            self.logger.error(
                final_error, extra={"job_name": job_name, "max_retries": max_retries}
            )

            return FlextResult.fail(final_error)

    # =============================================
    # PRIVATE METHODS
    # =============================================

    def _execute_meltano_pipeline(self, job_name: str) -> FlextResult[FlextTypes.Dict]:
        """Execute a Meltano pipeline using subprocess with comprehensive error handling.

        This method executes Meltano jobs via subprocess calls with proper environment
        setup, timeout handling, and structured error reporting.

        Args:
            job_name: Name of the Meltano job to execute

        Returns:
            FlextResult[Dict]: Railway-oriented result containing execution details
            or comprehensive error information.

        FLEXT OPTIMIZATION:
        - Uses FlextResult for railway-oriented error handling
        - Comprehensive environment setup
        - Timeout protection and proper cleanup
        - Structured logging and error reporting
        - Type-safe implementation

        """
        start_time = time.time()

        try:
            # Validate and sanitize job name
            sanitized_job_name = self._validate_job_name(job_name)
            self.logger.info(f"Executing Meltano job: {sanitized_job_name}")

            # Build execution environment
            env = self._build_meltano_environment()

            # Prepare Meltano command
            cmd = ["meltano", "run", sanitized_job_name]

            # Set working directory
            working_dir = Path(self.settings.meltano_project_root or ".")

            self.logger.debug(
                f"Meltano command: {' '.join(cmd)}",
                extra={
                    "job_name": sanitized_job_name,
                    "working_dir": str(working_dir),
                    "environment": self.settings.meltano_environment,
                },
            )

            # Execute Meltano job with timeout protection
            result = FlextUtilities.run_external_command(
                cmd,
                check=False,
                cwd=working_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.settings.pipeline_timeout_seconds,
            )

            execution_time = time.time() - start_time

            # Process execution results
            if result.returncode == 0:
                self.logger.info(
                    "Meltano job completed successfully",
                    extra={
                        "job_name": sanitized_job_name,
                        "execution_time": execution_time,
                        "return_code": result.returncode,
                    },
                )

                return FlextResult.ok({
                    "execution_time": execution_time,
                    "output": result.stdout.strip(),
                    "metadata": {
                        "return_code": result.returncode,
                        "stderr": result.stderr.strip(),
                        "job_name": sanitized_job_name,
                    },
                })
            error_msg = f"Meltano job failed with return code {result.returncode}"
            self.logger.error(
                error_msg,
                extra={
                    "job_name": sanitized_job_name,
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                },
            )

            return FlextResult.fail(error_msg)

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            timeout_error = f"Meltano job timed out after {execution_time:.2f}s"
            self.logger.exception(timeout_error, extra={"job_name": job_name})
            return FlextResult.fail(timeout_error)

        except FileNotFoundError:
            execution_time = time.time() - start_time
            meltano_error = (
                "Meltano executable not found. Ensure Meltano is installed and in PATH."
            )
            self.logger.exception(meltano_error, extra={"job_name": job_name})
            return FlextResult.fail(meltano_error)

        except Exception as e:
            execution_time = time.time() - start_time
            unexpected_error = f"Unexpected error during Meltano job execution: {e}"
            self.logger.exception(unexpected_error, extra={"job_name": job_name})
            return FlextResult.fail(unexpected_error)

    def _build_meltano_environment(self) -> FlextTypes.StringDict:
        """Build comprehensive environment variables for Meltano execution.

        Constructs a complete environment dictionary with all necessary configuration
        for Meltano pipeline execution, including Oracle WMS and database credentials.

        Returns:
            FlextTypes.StringDict: Environment variables dictionary for subprocess execution.

        FLEXT OPTIMIZATION:
        - Comprehensive environment setup
        - Type-safe configuration access
        - Proper credential handling
        - Structured logging integration

        """
        env = os.environ.copy()

        # Meltano core configuration
        env.update({
            "MELTANO_ENVIRONMENT": self.settings.meltano_environment,
            "MELTANO_PROJECT_ROOT": str(
                Path(self.settings.meltano_project_root or ".")
            ),
        })

        # Oracle WMS source configuration
        wms_config = self.settings.wms_source_config
        env.update({
            "TAP_ORACLE_WMS_BASE_URL": wms_config.get("base_url", ""),
            "TAP_ORACLE_WMS_USERNAME": wms_config.get("username", ""),
            "TAP_ORACLE_WMS_PASSWORD": wms_config.get("password", ""),
            "TAP_ORACLE_WMS_COMPANY_CODE": wms_config.get("company_code", ""),
            "TAP_ORACLE_WMS_FACILITY_CODE": wms_config.get("facility_code", ""),
        })

        # Oracle target database configuration
        oracle_config = self.settings.oracle_connection_config
        env.update({
            "FLEXT_TARGET_ORACLE_HOST": oracle_config.get("host", ""),
            "FLEXT_TARGET_ORACLE_PORT": str(oracle_config.get("port", "")),
            "FLEXT_TARGET_ORACLE_USERNAME": oracle_config.get("username", ""),
            "FLEXT_TARGET_ORACLE_PASSWORD": oracle_config.get("password", ""),
            "FLEXT_TARGET_ORACLE_SCHEMA": oracle_config.get("schema", ""),
        })

        # Handle service name vs SID (backward compatibility)
        if oracle_config.get("service_name"):
            env["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = oracle_config["service_name"]
        elif oracle_config.get("sid"):
            env["FLEXT_TARGET_ORACLE_SID"] = oracle_config["sid"]

        self.logger.debug(
            "Meltano environment configured",
            extra={
                "environment": self.settings.meltano_environment,
                "wms_base_url": wms_config.get("base_url", ""),
                "oracle_host": oracle_config.get("host", ""),
            },
        )

        return env

    def _validate_initial_configuration(self) -> FlextResult[None]:
        """Validate orchestrator configuration during initialization.

        Performs essential configuration validation required for orchestrator
        to function properly, ensuring all required settings are present.

        Returns:
            FlextResult[None]: Success if configuration is valid, failure with error details.

        FLEXT OPTIMIZATION:
        - Railway-oriented validation
        - Comprehensive error reporting
        - Structured logging

        """
        try:
            # Validate Meltano environment
            if not self.settings.meltano_environment:
                return FlextResult.fail("meltano_environment is required")

            # Validate project root exists
            project_root = Path(self.settings.meltano_project_root or ".")
            if not project_root.exists():
                return FlextResult.fail(
                    f"Meltano project root does not exist: {project_root}"
                )

            # Validate meltano.yml exists
            meltano_config = project_root / "meltano.yml"
            if not meltano_config.exists():
                return FlextResult.fail(
                    f"meltano.yml not found in project root: {project_root}"
                )

            # Validate pipeline timeout
            if self.settings.pipeline_timeout_seconds <= 0:
                return FlextResult.fail("pipeline_timeout_seconds must be positive")

            self.logger.debug("Initial configuration validation passed")
            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Configuration validation failed: {e}")

    def _validate_meltano_project(self) -> FlextResult[None]:
        """Validate Meltano project structure and configuration.

        Checks that the Meltano project is properly configured and all
        required files and settings are present.

        Returns:
            FlextResult[None]: Success if project is valid, failure with details.

        FLEXT OPTIMIZATION:
        - Comprehensive project validation
        - Detailed error reporting
        - Type-safe file operations

        """
        try:
            project_root = Path(self.settings.meltano_project_root or ".")

            # Check project structure
            required_files = ["meltano.yml", "requirements.txt"]
            for file_name in required_files:
                file_path = project_root / file_name
                if not file_path.exists():
                    return FlextResult.fail(f"Required file not found: {file_path}")

            # Check for meltano environment
            if not self.settings.meltano_environment:
                return FlextResult.fail("Meltano environment not configured")

            self.logger.debug("Meltano project validation passed")
            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Meltano project validation failed: {e}")

    def _validate_environment_configuration(self) -> FlextResult[None]:
        """Validate environment-specific configuration.

        Validates that all required environment variables and configuration
        settings are properly set for the current environment.

        Returns:
            FlextResult[None]: Success if environment config is valid, failure with details.

        FLEXT OPTIMIZATION:
        - Environment-aware validation
        - Comprehensive credential checking
        - Structured error reporting

        """
        try:
            # Validate WMS configuration
            wms_config = self.settings.wms_source_config
            required_wms_fields = ["base_url", "username", "password", "company_code"]
            for field in required_wms_fields:
                if not wms_config.get(field):
                    return FlextResult.fail(f"WMS {field} is required")

            # Validate Oracle configuration
            oracle_config = self.settings.oracle_connection_config
            required_oracle_fields = ["host", "port", "username", "password", "schema"]
            for field in required_oracle_fields:
                if not oracle_config.get(field):
                    return FlextResult.fail(f"Oracle {field} is required")

            # Validate port is valid
            try:
                port = int(oracle_config.get("port", 0))
                if port <= 0 or port > MAX_PORT_NUMBER:
                    return FlextResult.fail(
                        f"Oracle port must be between 1 and {MAX_PORT_NUMBER}"
                    )
            except (ValueError, TypeError):
                return FlextResult.fail("Oracle port must be a valid number")

            self.logger.debug("Environment configuration validation passed")
            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Environment configuration validation failed: {e}")

    def _validate_job_name(self, job_name: str) -> str:
        """Validate and sanitize job name to prevent command injection.

        Performs comprehensive validation of job names to ensure they are safe
        for use in subprocess calls and don't contain malicious characters.

        Args:
            job_name: Job name to validate and sanitize.

        Returns:
            str: Validated and sanitized job name.

        Raises:
            ValueError: If job_name is empty or contains invalid characters.

        Example:
            >>> orchestrator._validate_job_name("full-sync-job")
            'full-sync-job'

        FLEXT OPTIMIZATION:
        - Comprehensive input validation
        - Command injection prevention
        - Type-safe string handling
        - Structured error messages

        """
        if not job_name or not job_name.strip():
            error_msg = "Job name cannot be empty or whitespace-only"
            self.logger.error(error_msg, extra={"job_name": repr(job_name)})
            raise ValueError(error_msg)

        sanitized_job_name = job_name.strip()

        # Define forbidden characters that could be used for command injection
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
            error_msg = f"Job name contains invalid characters: {sanitized_job_name}"
            self.logger.error(error_msg, extra={"job_name": sanitized_job_name})
            raise ValueError(error_msg)

        # Additional validation: reasonable length
        if len(sanitized_job_name) > MAX_JOB_NAME_LENGTH:
            error_msg = f"Job name too long (max {MAX_JOB_NAME_LENGTH} chars): {len(sanitized_job_name)}"
            self.logger.error(error_msg, extra={"job_name": sanitized_job_name})
            raise ValueError(error_msg)

        self.logger.debug(f"Job name validated: {sanitized_job_name}")
        return sanitized_job_name

    # =============================================
    # FACTORY METHODS - FLEXT PATTERN
    # =============================================

    @classmethod
    def create_orchestrator(
        cls,
        settings: GruponosMeltanoNativeConfig | None = None,
    ) -> GruponosMeltanoOrchestrator:
        """Create configured instance of GrupoNOS Meltano Orchestrator.

        Factory method for creating fully configured orchestrator instances
        with proper initialization and validation.

        Args:
            settings: Optional GruponosMeltanoNativeConfig instance.
                     If None, configuration will be loaded from environment.

        Returns:
            GruponosMeltanoOrchestrator: Fully configured orchestrator instance.

        Example:
            >>> orchestrator = GruponosMeltanoOrchestrator.create_orchestrator()
            >>> result = orchestrator.validate_configuration()
            >>> assert result.is_success

        FLEXT OPTIMIZATION:
        - Class method factory pattern
        - Comprehensive documentation
        - Type-safe configuration handling

        """
        return cls(settings)

    @classmethod
    def create_pipeline_runner(
        cls,
        settings: GruponosMeltanoNativeConfig | None = None,
    ) -> GruponosMeltanoOrchestrator._PipelineRunner:
        """Create configured instance of GrupoNOS pipeline runner.

        Factory method for creating pipeline runner instances with retry logic
        and comprehensive error handling.

        Args:
            settings: Optional GruponosMeltanoNativeConfig instance.
                     If None, configuration will be loaded from environment.

        Returns:
            GruponosMeltanoOrchestrator._PipelineRunner: Configured pipeline runner instance.

        Example:
            >>> runner = GruponosMeltanoOrchestrator.create_pipeline_runner()
            >>> result = runner.run_with_retry("full-sync-job")
            >>> assert result.is_success

        FLEXT OPTIMIZATION:
        - Class method factory pattern
        - Proper encapsulation of nested classes
        - Type-safe instance creation

        """
        orchestrator = cls(settings)
        return cls._PipelineRunner(orchestrator)


# =============================================
# BACKWARD COMPATIBILITY FUNCTIONS
# =============================================


def create_gruponos_meltano_orchestrator(
    settings: GruponosMeltanoNativeConfig | None = None,
) -> GruponosMeltanoOrchestrator:
    """Create GrupoNOS Meltano Orchestrator instance (backward compatibility).

    Args:
        settings: Optional GruponosMeltanoNativeConfig instance.

    Returns:
        GruponosMeltanoOrchestrator: Configured orchestrator instance.

    Note:
        This function is maintained for backward compatibility.
        Use GruponosMeltanoOrchestrator.create_orchestrator() for new code.

    """
    return GruponosMeltanoOrchestrator.create_orchestrator(settings)


def create_gruponos_meltano_pipeline_runner(
    settings: GruponosMeltanoNativeConfig | None = None,
) -> GruponosMeltanoOrchestrator._PipelineRunner:
    """Create GrupoNOS pipeline runner instance (backward compatibility).

    Args:
        settings: Optional GruponosMeltanoNativeConfig instance.

    Returns:
        GruponosMeltanoOrchestrator._PipelineRunner: Configured pipeline runner instance.

    Note:
        This function is maintained for backward compatibility.
        Use GruponosMeltanoOrchestrator.create_pipeline_runner() for new code.

    """
    return GruponosMeltanoOrchestrator.create_pipeline_runner(settings)


# =============================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================

# Type aliases for backward compatibility
GruponosMeltanoPipelineResult = GruponosMeltanoModels.PipelineResult

# Module-level exports with comprehensive API surface
__all__: FlextTypes.StringList = [
    "GruponosMeltanoModels",
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineResult",
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
]
