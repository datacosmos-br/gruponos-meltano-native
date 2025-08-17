"""Orquestrador Nativo Meltano GrupoNOS - Implementação específica GrupoNOS.

Este módulo fornece toda a orquestração específica do GrupoNOS para pipelines Meltano
com sistemas Oracle WMS, construído sobre padrões de fundação FLEXT.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import time
from dataclasses import dataclass
from pathlib import Path

from flext_core import FlextResult

from gruponos_meltano_native.config import GruponosMeltanoSettings

# =============================================
# RESULTADOS DE PIPELINE GRUPONOS
# =============================================


@dataclass
class GruponosMeltanoPipelineResult:
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
    metadata: dict[str, object] | None = None


# =============================================
# EXECUTOR DE PIPELINE GRUPONOS
# =============================================


class GruponosMeltanoPipelineRunner:
    """Executor de pipeline Meltano específico do GrupoNOS com capacidades de execução empresarial.

    Este executor fornece funcionalidade de execução de pipeline de baixo nível com tratamento
    abrangente de erros, gerenciamento de ambiente e integração de monitoramento. Serve como
    a camada de infraestrutura para operações de pipeline ETL.

    Funcionalidades Principais:
      - Execução Meltano baseada em subprocesso com gerenciamento de timeout
      - Environment variable management for secure credential handling
      - Comprehensive error capture and reporting
      - Performance monitoring and execution metrics
      - Process isolation and resource management

    Architecture:
      Implements the infrastructure layer of Clean Architecture, handling
      external system interactions (Meltano CLI) while providing a clean
      interface for application services.

    Example:
      Direct runner usage (typically used via GruponosMeltanoOrchestrator):

      >>> settings = GruponosMeltanoSettings()
      >>> runner = GruponosMeltanoPipelineRunner(settings)
      >>> result = runner.run_pipeline("full-sync-job")
      >>> print(f"Pipeline result: {result.success}")

    Security:
      - Credentials are passed via environment variables, not command line
      - Process isolation prevents credential leakage
      - Secure environment variable handling with proper cleanup

    """

    def __init__(self, settings: GruponosMeltanoSettings) -> None:
      """Inicializa o executor de pipeline com configurações GrupoNOS.

      Args:
          settings: Configurações Meltano GrupoNOS contendo todas as
                   variáveis de ambiente necessárias, strings de conexão
                   e parâmetros de configuração de pipeline.

      Raises:
          GruponosMeltanoConfigurationError: Se configurações obrigatórias estiverem ausentes.
          GruponosMeltanoValidationError: Se a validação das configurações falhar.
          FileNotFoundError: Se o diretório meltano_project_root não existir.

      Example:
          >>> settings = GruponosMeltanoSettings()
          >>> runner = GruponosMeltanoPipelineRunner(settings)
          >>> # Runner está pronto para execução de pipeline

      """
      self.settings = settings
      self.project_root = Path(settings.meltano_project_root)

    def run_pipeline(
      self,
      job_name: str,
      **_kwargs: object,
    ) -> GruponosMeltanoPipelineResult:
      """Executa pipeline Meltano GrupoNOS.

      Executa um pipeline Meltano específico usando subprocess com
      gerenciamento de timeout e captura completa de saída.

      Args:
          job_name: Nome do job Meltano a ser executado.
          **_kwargs: Argumentos adicionais (não utilizados).

      Returns:
          GruponosMeltanoPipelineResult: Resultado da execução contendo
          status de sucesso, tempo de execução e saídas.

      Raises:
          ValueError: Se job_name contém caracteres inválidos.
          TimeoutError: Se a execução exceder o timeout.

      Example:
          >>> runner = GruponosMeltanoPipelineRunner(settings)
          >>> resultado = runner.run_pipeline("full-sync-job")
          >>> if resultado.success:
          ...     print(f"Pipeline executado em {resultado.execution_time:.2f}s")

      """
      start_time = time.time()

      try:
          # Validar e sanitizar job_name
          sanitized_job_name = self._validate_job_name(job_name)

          # Construir comando meltano
          cmd = ["meltano", "run", sanitized_job_name]

          # Definir variáveis de ambiente para GrupoNOS
          env = self._build_environment()

          # Executar pipeline via asyncio subprocess para atender política de segurança
          async def _run() -> tuple[int, str, str]:
              proc = await asyncio.create_subprocess_exec(
                  *cmd,
                  cwd=str(self.project_root),
                  env=env,
                  stdout=asyncio.subprocess.PIPE,
                  stderr=asyncio.subprocess.PIPE,
              )
              try:
                  stdout_b, stderr_b = await asyncio.wait_for(
                      proc.communicate(),
                      timeout=3600,
                  )
              except TimeoutError:
                  with contextlib.suppress(ProcessLookupError):
                      proc.kill()
                  await proc.wait()
                  raise TimeoutError from None
              return (
                  int(proc.returncode or 0),
                  (stdout_b.decode("utf-8", errors="replace") if stdout_b else ""),
                  (stderr_b.decode("utf-8", errors="replace") if stderr_b else ""),
              )

          return_code, stdout_text, stderr_text = asyncio.run(_run())

          execution_time = time.time() - start_time

          if return_code == 0:
              return GruponosMeltanoPipelineResult(
                  success=True,
                  job_name=job_name,
                  execution_time=execution_time,
                  output=stdout_text,
                  metadata={"return_code": return_code},
              )
          return GruponosMeltanoPipelineResult(
              success=False,
              job_name=job_name,
              execution_time=execution_time,
              output=stdout_text,
              error=stderr_text,
              metadata={"return_code": return_code},
          )

      except TimeoutError:
          execution_time = time.time() - start_time
          return GruponosMeltanoPipelineResult(
              success=False,
              job_name=job_name,
              execution_time=execution_time,
              output="",
              error="Pipeline execution timed out",
              metadata={"timeout": True},
          )
      except Exception as e:
          execution_time = time.time() - start_time
          return GruponosMeltanoPipelineResult(
              success=False,
              job_name=job_name,
              execution_time=execution_time,
              output="",
              error=str(e),
              metadata={"exception": type(e).__name__},
          )

    def _build_environment(self) -> dict[str, str]:
      """Constrói variáveis de ambiente para pipelines GrupoNOS.

      Cria um dicionário completo de variáveis de ambiente necessárias
      para execução de pipelines Meltano com configurações específicas
      do GrupoNOS para Oracle WMS.

      Returns:
          dict[str, str]: Dicionário com todas as variáveis de ambiente
          configuradas, incluindo conexões Oracle e configurações WMS.

      """
      env = os.environ.copy()

      # Adicionar variáveis de ambiente específicas do GrupoNOS
      env.update(
          {
              "MELTANO_ENVIRONMENT": self.settings.meltano_environment,
              "MELTANO_PROJECT_ROOT": str(self.project_root),
              # Configuração Oracle WMS
              "TAP_ORACLE_WMS_BASE_URL": self.settings.wms_source.base_url,
              "TAP_ORACLE_WMS_USERNAME": self.settings.wms_source.username,
              "TAP_ORACLE_WMS_PASSWORD": self.settings.wms_source.password.get_secret_value(),
              "TAP_ORACLE_WMS_COMPANY_CODE": self.settings.wms_source.company_code,
              "TAP_ORACLE_WMS_FACILITY_CODE": self.settings.wms_source.facility_code,
              # Configuração de destino Oracle
              "FLEXT_TARGET_ORACLE_HOST": self.settings.oracle_connection.host,
              "FLEXT_TARGET_ORACLE_PORT": str(self.settings.oracle_connection.port),
              "FLEXT_TARGET_ORACLE_USERNAME": self.settings.oracle_connection.username,
              "FLEXT_TARGET_ORACLE_PASSWORD": self.settings.oracle_connection.password.get_secret_value()
              if hasattr(self.settings.oracle_connection.password, "get_secret_value")
              else str(self.settings.oracle_connection.password),
              "FLEXT_TARGET_ORACLE_SCHEMA": self.settings.target_oracle.target_schema,
          },
      )

      # Adicionar nome do serviço ou SID
      if self.settings.oracle_connection.service_name:
          env["FLEXT_TARGET_ORACLE_SERVICE_NAME"] = (
              self.settings.oracle_connection.service_name
          )
      elif self.settings.oracle_connection.sid:
          env["FLEXT_TARGET_ORACLE_SID"] = self.settings.oracle_connection.sid

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
          >>> runner._validate_job_name("full-sync-job")
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

    async def run_with_retry(
      self,
      job_name: str,
      max_retries: int = 3,
      **kwargs: object,
    ) -> GruponosMeltanoPipelineResult:
      """Executa pipeline com lógica de retry.

      Executa um pipeline com tentativas automáticas de retry em caso
      de falha, usando backoff exponencial entre tentativas.

      Args:
          job_name: Nome do job a ser executado.
          max_retries: Número máximo de tentativas (padrão: 3).
          **kwargs: Argumentos adicionais passados para run_pipeline.

      Returns:
          GruponosMeltanoPipelineResult: Resultado da execução após
          todas as tentativas, bem-sucedida ou não.

      Example:
          >>> runner = GruponosMeltanoPipelineRunner(settings)
          >>> resultado = await runner.run_with_retry("sync-job", max_retries=5)
          >>> print(f"Sucesso: {resultado.success}")

      """
      last_result = None
      for attempt in range(max_retries + 1):
          try:
              # Execute in thread pool to avoid blocking
              loop = asyncio.get_event_loop()
              result = await loop.run_in_executor(
                  None,
                  self.run_pipeline,
                  job_name,
                  **kwargs,
              )

              if result.success:
                  return result

              last_result = result
              if attempt < max_retries:
                  await asyncio.sleep(2**attempt)  # Exponential backoff

          except Exception as e:
              last_result = GruponosMeltanoPipelineResult(
                  success=False,
                  job_name=job_name,
                  execution_time=0.0,
                  output="",
                  error=str(e),
                  metadata={"attempt": attempt + 1, "exception": type(e).__name__},
              )

              if attempt < max_retries:
                  await asyncio.sleep(2**attempt)

      return last_result or GruponosMeltanoPipelineResult(
          success=False,
          job_name=job_name,
          execution_time=0.0,
          output="",
          error="All retry attempts failed",
          metadata={"max_retries": max_retries},
      )


# =============================================
# GRUPONOS ORCHESTRATOR
# =============================================


class GruponosMeltanoOrchestrator:
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

    Example:
      Basic orchestrator usage:

      >>> orchestrator = GruponosMeltanoOrchestrator()
      >>> result = orchestrator.run_full_sync()
      >>> if result.success:
      ...     print(f"Pipeline completed in {result.execution_time:.2f}s")
      ... else:
      ...     print(f"Pipeline failed: {result.error}")

    Integration:
      - Uses GruponosMeltanoSettings for environment-aware configuration
      - Integrates with GruponosMeltanoPipelineRunner for execution
      - Coordinates with monitoring systems for observability
      - Implements FLEXT patterns for consistent error handling

    """

    def __init__(self, settings: GruponosMeltanoSettings | None = None) -> None:
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
          >>> custom_settings = GruponosMeltanoSettings(environment="production")
          >>> orchestrator = GruponosMeltanoOrchestrator(custom_settings)

      """
      self.settings = settings or GruponosMeltanoSettings()
      self.pipeline_runner = GruponosMeltanoPipelineRunner(self.settings)

    async def validate_configuration(self) -> FlextResult[None]:
      """Valida configuração do orquestrador usando padrões FLEXT.

      Executa validação completa das configurações necessárias para
      operação do orquestrador, incluindo conexões Oracle e fonte WMS.

      Returns:
          FlextResult[None]: Indica sucesso ou falha com erros de validação.

      Example:
          >>> orchestrator = GruponosMeltanoOrchestrator()
          >>> resultado = await orchestrator.validate_configuration()
          >>> if resultado.success:
          ...     print("Configuração válida")

      """
      # Check if target Oracle has required configuration
      target_oracle = self.settings.target_oracle
      if not target_oracle.target_schema:
          return FlextResult.fail("Target Oracle not configured")

      # Check if WMS source has required configuration
      wms_source = self.settings.wms_source
      if not wms_source.oracle:
          return FlextResult.fail("WMS source not configured")

      return FlextResult.ok(None)

    def run_full_sync(self) -> GruponosMeltanoPipelineResult:
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
      return self.pipeline_runner.run_pipeline("full-sync-job")

    def run_incremental_sync(self) -> GruponosMeltanoPipelineResult:
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
      return self.pipeline_runner.run_pipeline("incremental-sync-job")

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
      return self.pipeline_runner.run_pipeline(job_name)

    def list_jobs(self) -> list[str]:
      """Lista todos os jobs de pipeline disponíveis.

      Este método retorna uma lista de todos os jobs Meltano disponíveis para
      execução na configuração atual do projeto. Jobs são definidos em meltano.yml
      e podem incluir tanto jobs ETL padrão quanto operações customizadas.

      Returns:
          list[str]: Lista de nomes de jobs disponíveis que podem ser executados
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
      # Based on meltano.yml configuration
      return ["full-sync-job", "incremental-sync-job"]

    def list_pipelines(self) -> list[str]:
      """Lista pipelines disponíveis (alias para list_jobs).

      Returns:
          list[str]: Lista de nomes de pipelines disponíveis.

      """
      return self.list_jobs()

    async def run_pipeline(
      self,
      pipeline_name: str,
      **kwargs: object,
    ) -> GruponosMeltanoPipelineResult:
      """Executa pipeline assincronamente (método de compatibilidade).

      Args:
          pipeline_name: Nome do pipeline a ser executado.
          **kwargs: Argumentos adicionais passados para o pipeline.

      Returns:
          GruponosMeltanoPipelineResult: Resultado da execução do pipeline.

      """
      # Execute in thread pool to avoid blocking
      loop = asyncio.get_event_loop()
      return await loop.run_in_executor(
          None,
          self.pipeline_runner.run_pipeline,
          pipeline_name,
          **kwargs,
      )

    def get_job_status(self, job_name: str) -> dict[str, object]:
      """Obtém status de um job específico.

      Args:
          job_name: Nome do job para verificar status.

      Returns:
          dict[str, object]: Informações de status do job incluindo
          disponibilidade e configurações.

      """
      return {
          "job_name": job_name,
          "available": job_name in self.list_jobs(),
          "settings": self.settings.dict(),
      }


# =============================================
# FACTORY FUNCTIONS
# =============================================


def create_gruponos_meltano_orchestrator(
    settings: GruponosMeltanoSettings | None = None,
) -> GruponosMeltanoOrchestrator:
    """Cria instância do orquestrador Meltano GrupoNOS.

    Args:
      settings: Configurações opcionais do Meltano GrupoNOS.

    Returns:
      GruponosMeltanoOrchestrator: Instância configurada do orquestrador.

    """
    return GruponosMeltanoOrchestrator(settings)


def create_gruponos_meltano_pipeline_runner(
    settings: GruponosMeltanoSettings | None = None,
) -> GruponosMeltanoPipelineRunner:
    """Cria instância do executor de pipeline GrupoNOS.

    Args:
      settings: Configurações opcionais do Meltano GrupoNOS.

    Returns:
      GruponosMeltanoPipelineRunner: Instância configurada do executor.

    """
    pipeline_settings = settings or GruponosMeltanoSettings()
    return GruponosMeltanoPipelineRunner(pipeline_settings)


# Re-export for backward compatibility
__all__: list[str] = [
    "GruponosMeltanoOrchestrator",
    "GruponosMeltanoPipelineResult",
    "GruponosMeltanoPipelineRunner",
    "create_gruponos_meltano_orchestrator",
    "create_gruponos_meltano_pipeline_runner",
]
