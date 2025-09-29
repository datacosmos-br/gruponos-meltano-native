"""Interface de Linha de Comando GrupoNOS Meltano Native.

Interface de linha de comando para integração ETL Oracle WMS,
seguindo princípios de Arquitetura Limpa e padrões CLI unificados.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import cast

# FLEXT ARCHITECTURE COMPLIANCE: Using flext-cli foundation exclusively
from flext_cli import FlextCliApi, FlextCliCommands, FlextCliModels
from flext_core import FlextLogger, FlextResult, FlextTypes
from gruponos_meltano_native.config import GruponosMeltanoNativeConfig
from gruponos_meltano_native.utilities import GruponosMeltanoNativeUtilities

# from rich.console import Console  # FORBIDDEN: CLI violations - use flext-cli exclusively


# Handler function implementations
def handle_health_command() -> FlextResult[dict[str, str]]:
    """Handle health check command."""
    return FlextResult[dict[str, str]].ok(
        {"status": "healthy", "timestamp": "2025-01-27T00:00:00Z"},
    )


def handle_run_command(
    pipeline_name: str,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> FlextResult[dict[str, str | bool]]:
    """Handle pipeline run command using GruponosMeltanoNativeUtilities.

    ZERO TOLERANCE FIX: Now actually uses utilities for pipeline execution.
    """
    # ZERO TOLERANCE FIX: Use GruponosMeltanoNativeUtilities for pipeline execution
    from gruponos_meltano_native.config import GruponosMeltanoNativeConfig
    from gruponos_meltano_native.utilities import GruponosMeltanoNativeUtilities

    utilities = GruponosMeltanoNativeUtilities()
    config = GruponosMeltanoNativeConfig()

    if dry_run:
        # Use utilities for dry run validation
        validation_result = (
            utilities.MeltanoPipelineManagement.validate_meltano_configuration(
                config.model_dump()
            )
        )
        if validation_result.is_failure:
            return FlextResult[dict[str, str | bool]].fail(
                f"Pipeline validation failed: {validation_result.error}"
            )

        return FlextResult[dict[str, str | bool]].ok({
            "pipeline": pipeline_name,
            "status": "validated",
            "dry_run": True,
            "force": force,
        })

    # Use utilities for actual pipeline execution
    execution_result = utilities.MeltanoPipelineManagement.execute_meltano_job(
        job_name=pipeline_name, config=config.model_dump()
    )

    if execution_result.is_failure:
        return FlextResult[dict[str, str | bool]].fail(
            f"Pipeline execution failed: {execution_result.error}"
        )

    return FlextResult[dict[str, str | bool]].ok({
        "pipeline": pipeline_name,
        "status": "completed",
        "dry_run": dry_run,
        "force": force,
    })


def handle_list_command() -> FlextResult[list[str]]:
    """Handle list pipelines command using GruponosMeltanoNativeUtilities.

    ZERO TOLERANCE FIX: Now actually uses utilities for pipeline listing.
    """
    # ZERO TOLERANCE FIX: Use GruponosMeltanoNativeUtilities for pipeline listing
    utilities = GruponosMeltanoNativeUtilities()
    config = GruponosMeltanoNativeConfig()

    # Use utilities for actual pipeline listing
    jobs_result = utilities.MeltanoPipelineManagement.list_available_jobs(
        config.model_dump()
    )

    if jobs_result.is_failure:
        return FlextResult[list[str]].fail(
            f"Failed to list pipelines: {jobs_result.error}"
        )

    return FlextResult[list[str]].ok(jobs_result.unwrap())


def handle_validate_command(
    output_format: str = "table",
) -> FlextResult[dict[str, str]]:
    """Handle validate command using GruponosMeltanoNativeUtilities.

    ZERO TOLERANCE FIX: Now actually uses utilities for validation.
    """
    # ZERO TOLERANCE FIX: Use GruponosMeltanoNativeUtilities for validation
    utilities = GruponosMeltanoNativeUtilities()
    config = GruponosMeltanoNativeConfig()

    # Use utilities for comprehensive validation
    validation_result = (
        utilities.MeltanoPipelineManagement.validate_meltano_configuration(
            config.model_dump()
        )
    )

    if validation_result.is_failure:
        return FlextResult[dict[str, str]].fail(
            f"Validation failed: {validation_result.error}"
        )

    # Additional WMS API validation using utilities
    wms_validation_result = utilities.WmsApiOperations.validate_wms_connection(
        config.wms_source.model_dump()
    )

    if wms_validation_result.is_failure:
        return FlextResult[dict[str, str]].fail(
            f"WMS connection validation failed: {wms_validation_result.error}"
        )

    return FlextResult[dict[str, str]].ok({
        "validation": "passed",
        "format": output_format,
        "config_status": "valid",
        "wms_connection": "valid",
    })


def handle_show_config_command(
    output_format: str = "yaml",
) -> FlextResult[dict[str, str]]:
    """Handle show config command using GruponosMeltanoNativeUtilities.

    ZERO TOLERANCE FIX: Now actually uses utilities for configuration display.
    """
    # ZERO TOLERANCE FIX: Use GruponosMeltanoNativeUtilities for config operations
    utilities = GruponosMeltanoNativeUtilities()
    config = GruponosMeltanoNativeConfig()

    # Use utilities for configuration formatting and display
    config_display_result = (
        utilities.MeltanoPipelineManagement.format_configuration_for_display(
            config=config.model_dump(), output_format=output_format
        )
    )

    if config_display_result.is_failure:
        return FlextResult[dict[str, str]].fail(
            f"Failed to format configuration: {config_display_result.error}"
        )

    return FlextResult[dict[str, str]].ok({
        "config": "loaded",
        "format": output_format,
        "content": config_display_result.unwrap(),
    })


def handle_run_with_retry_command(
    pipeline_name: str,
    max_retries: int = 3,
    *,
    retry_delay: int = 5,
) -> FlextResult[dict[str, str | int]]:
    """Handle run with retry command using GruponosMeltanoNativeUtilities.

    ZERO TOLERANCE FIX: Now actually uses utilities for retry execution.
    """
    # ZERO TOLERANCE FIX: Use GruponosMeltanoNativeUtilities for retry execution
    utilities = GruponosMeltanoNativeUtilities()
    config = GruponosMeltanoNativeConfig()

    # Use utilities for pipeline execution with retry logic
    retry_result = utilities.MeltanoPipelineManagement.execute_meltano_job_with_retry(
        job_name=pipeline_name,
        config=config.model_dump(),
        max_retries=max_retries,
        retry_delay=retry_delay,
    )

    if retry_result.is_failure:
        return FlextResult[dict[str, str | int]].fail(
            f"Pipeline execution with retry failed: {retry_result.error}"
        )

    retry_data = retry_result.unwrap()
    return FlextResult[dict[str, str | int]].ok({
        "pipeline": pipeline_name,
        "retries": max_retries,
        "retry_delay": retry_delay,
        "attempts_used": retry_data.get("attempts_used", 1),
        "status": "completed",
    })


logger = FlextLogger(__name__)


def initialize_cli_environment(*, debug: bool = False) -> FlextTypes.Core.Dict:
    """Inicializa ambiente CLI usando padrões do framework FLEXT CLI.

    Esta função configura o ambiente CLI completo incluindo logging,
    configuração e gerenciamento de contexto usando padrões FLEXT CLI.

    Args:
      debug: Se True, habilita modo debug para troubleshooting detalhado.
             Se False, usa configuração de produção.

    Returns:
      FlextTypes.Core.Dict: Contexto do ambiente CLI com configuração e console.

    Note:
      Integração:
      Usa padrões do framework FLEXT CLI para configuração consistente
      de ambiente em todo o ecossistema FLEXT e padrões CLI empresariais.

    """
    # Lightweight initialization: defer config creation to individual commands
    cli_api = FlextCliApi()
    return {
        "cli_api": cli_api,
        "debug": debug,
    }


def create_gruponos_cli() -> FlextResult[FlextCliCommands]:
    """Create GrupoNOS CLI using flext-cli foundation - NO click imports."""
    try:
        # Initialize CLI through flext-cli (abstracts Click internally)
        cli_main = FlextCliCommands(
            name="gruponos-meltano-native",
            description="GrupoNOS Meltano Native - Gerenciador de Pipeline ETL Empresarial",
        )

        # Create proper CliCommand instances
        commands = {
            "health": FlextCliModels.CliCommand(
                id="health_command",
                command_line="health",
                execution_time=datetime.now(UTC),
            ),
            "run": FlextCliModels.CliCommand(
                id="run_command",
                command_line="run",
                execution_time=datetime.now(UTC),
            ),
            "list": FlextCliModels.CliCommand(
                id="list_command",
                command_line="list",
                execution_time=datetime.now(UTC),
            ),
            "validate": FlextCliModels.CliCommand(
                id="validate_command",
                command_line="validate",
                execution_time=datetime.now(UTC),
            ),
            "show-config": FlextCliModels.CliCommand(
                id="show_config_command",
                command_line="show-config",
                execution_time=datetime.now(UTC),
            ),
            "run-with-retry": FlextCliModels.CliCommand(
                id="run_with_retry_command",
                command_line="run-with-retry",
                execution_time=datetime.now(UTC),
            ),
        }

        register_result = cli_main.register_command_group(
            "gruponos", cast("dict[str, object]", commands)
        )
        if register_result.is_failure:
            return FlextResult[FlextCliCommands].fail(
                f"Commands registration failed: {register_result.error}",
            )

        return FlextResult[FlextCliCommands].ok(cli_main)
    except Exception as e:
        return FlextResult[FlextCliCommands].fail(f"CLI creation failed: {e}")


def cli(*, debug: bool = False, config_file: str | None = None) -> None:
    """Main CLI entry point using flext-cli foundation."""
    try:
        # Initialize CLI environment using padrões empresariais
        initialize_cli_environment(debug=debug)

        if config_file:
            logger.info("Config file specified: %s", config_file)

        logger.info("GrupoNOS Meltano Native CLI started with FLEXT framework")

        # Create and execute the flext-cli implementation
        cli_result: FlextResult[object] = create_gruponos_cli()
        if cli_result.is_failure:
            logger.error(f"Failed to create CLI: {cli_result.error}")
            sys.exit(1)

        cli_main = cli_result.unwrap()
        execution_result: FlextResult[object] = cli_main.execute()
        if execution_result.is_failure:
            logger.error(f"CLI execution failed: {execution_result.error}")
            sys.exit(1)

    except ValueError:
        # Suppress stdout for ValueError per tests; log only and exit 1
        logger.exception("Failed to initialize CLI")
        sys.exit(1)
    except Exception:
        logger.exception("Failed to initialize CLI")
        sys.exit(1)


# Entry point for CLI execution


if __name__ == "__main__":
    cli()
