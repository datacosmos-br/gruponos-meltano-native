"""GrupoNOS Meltano Native CLI - FLEXT CLI Framework Integration.

Command-line interface using FLEXT CLI framework following FLEXT standards,
Clean Architecture principles, and unified CLI patterns across the ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import json
import sys

import click
import yaml

# FLEXT CLI Framework Integration
from flext_core import FlextResult, get_logger
from rich.console import Console

from gruponos_meltano_native.config import (
    GruponosMeltanoSettings,
    create_gruponos_meltano_settings,
)
from gruponos_meltano_native.orchestrator import (
    create_gruponos_meltano_orchestrator,
    create_gruponos_meltano_pipeline_runner,
)

logger = get_logger(__name__)


def initialize_cli_environment(*, debug: bool = False) -> dict[str, object]:
    """Initialize CLI environment using FLEXT CLI framework patterns.

    This function sets up the complete CLI environment including logging,
    configuration, and context management using FLEXT CLI standards.

    Args:
        debug: If True, enables debug mode for detailed troubleshooting.
               If False, uses production configuration.

    Returns:
        dict: CLI environment context with configuration and console.

    Integration:
        Uses FLEXT CLI framework patterns for consistent environment setup
        across the FLEXT ecosystem and enterprise CLI standards.

    """
    # Create CLI environment using flext-cli patterns
    cli_config = create_gruponos_meltano_settings()  # Use gruponos config utility

    console = Console()

    # Create a proper CLI context dict
    return {
        "config": cli_config,
        "console": console,
        "debug": debug or cli_config.debug,
    }


@click.group()
@click.version_option(version="0.9.0")
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.pass_context
def cli(
    ctx: click.Context,
    *,
    debug: bool,
    config_file: str | None,
) -> None:
    """GrupoNOS Meltano Native - Enterprise ETL Pipeline Manager.

    A FLEXT-standardized tool for managing Meltano pipelines with Oracle
    integration, comprehensive monitoring, and enterprise-grade reliability.
    """
    try:
        # Initialize CLI environment using FLEXT patterns
        cli_context = initialize_cli_environment(debug=debug)

        # Note: config_file handling will be implemented in future sprint
        # Current implementation focuses on core CLI framework integration

        # Store enhanced context
        ctx.ensure_object(dict)
        ctx.obj["cli_context"] = cli_context
        ctx.obj["debug"] = debug
        ctx.obj["config_file"] = config_file

        logger.info("GrupoNOS Meltano Native CLI started with FLEXT framework")

    except Exception:
        logger.exception("Failed to initialize CLI")
        sys.exit(1)


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check pipeline health and system connectivity."""
    try:
        cli_context: dict[str, object] = ctx.obj["cli_context"]
        console = cli_context["console"]
        logger.info("Starting health check with FLEXT CLI framework")

        # Create configuration using FLEXT patterns
        config_result = _create_configuration()
        if config_result.is_failure:
            logger.error("Configuration creation failed: %s", config_result.error)
            sys.exit(1)

        if config_result.data is None:
            logger.error("Configuration data is None")
            sys.exit(1)

        config = config_result.data
        health_status = {"configuration": "✅ Valid"}

        # Create orchestrator using FLEXT patterns
        orchestrator_result = _create_orchestrator(config)
        if orchestrator_result.is_failure:
            logger.error("Orchestrator creation failed: %s", orchestrator_result.error)
            health_status["orchestrator"] = "❌ Failed"
        else:
            health_status["orchestrator"] = "✅ Initialized"

        # Check Oracle connection
        oracle_status = _check_oracle_connection(config)
        health_status["oracle_connection"] = oracle_status

        # Check Meltano configuration
        meltano_status = _check_meltano_configuration(config)
        health_status["meltano_project"] = meltano_status

        # Format output using Rich console
        if isinstance(console, Console):
            console.print("📋 Health Check Results:")
            for component, status in health_status.items():
                console.print(f"  {component.ljust(20)}: {status}")

        logger.info("Health check completed successfully")

    except Exception as e:
        logger.exception("Health check failed")
        console = Console()
        console.print(f"❌ Health check failed: {e}")
        sys.exit(1)


def _create_configuration() -> FlextResult[GruponosMeltanoSettings]:
    """Create configuration using FLEXT patterns."""
    try:
        config = create_gruponos_meltano_settings()
        return FlextResult.ok(config)
    except Exception as e:
        return FlextResult.fail(f"Configuration creation failed: {e}")


def _create_orchestrator(config: GruponosMeltanoSettings) -> FlextResult[object]:
    """Create orchestrator using FLEXT patterns."""
    try:
        orchestrator = create_gruponos_meltano_orchestrator(config)
        return FlextResult.ok(orchestrator)
    except Exception as e:
        return FlextResult.fail(f"Orchestrator creation failed: {e}")


def _check_oracle_connection(config: GruponosMeltanoSettings) -> str:
    """Check Oracle connection status."""
    if (
        config.oracle
        and config.oracle.host
        and config.oracle.username
        and config.oracle.password
    ):
        return "✅ Configured"
    return "⚠️  Not fully configured"


def _check_meltano_configuration(config: GruponosMeltanoSettings) -> str:
    """Check Meltano configuration status."""
    if config.meltano_project_root and config.meltano_environment:
        return "✅ Found"
    return "⚠️  Missing"


@cli.command()
@click.argument("pipeline_name")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without executing",
)
@click.option(
    "--retry-attempts",
    type=int,
    default=3,
    help="Number of retry attempts on failure",
)
@click.pass_context
def run(
    _ctx: click.Context,
    pipeline_name: str,
    *,
    dry_run: bool,
    _retry_attempts: int,
) -> None:
    """Run a specific Meltano pipeline.

    PIPELINE_NAME: Name of the pipeline to execute
    """
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No actual changes will be made")
        logger.info("Running in dry-run mode")
        return

    click.echo(f"🚀 Starting pipeline: {pipeline_name}")
    logger.info("Starting pipeline execution: %s", pipeline_name)

    try:
        # Create configuration and orchestrator
        config = create_gruponos_meltano_settings()
        orchestrator = create_gruponos_meltano_orchestrator(config)

        async def run_pipeline() -> None:
            """Run the pipeline asynchronously."""
            result = await orchestrator.run_pipeline(pipeline_name)

            if result.success:
                click.echo("✅ Pipeline completed successfully!")
                click.echo(f"   Job: {result.job_name}")
                click.echo(f"   Execution time: {result.execution_time:.2f}s")
                if result.output:
                    click.echo(f"   Output: {result.output[:200]}...")
            else:
                click.echo(f"❌ Pipeline failed: {result.error or 'Unknown error'}")
                click.echo(f"   Job: {result.job_name}")
                click.echo(f"   Execution time: {result.execution_time:.2f}s")
                if result.output:
                    click.echo(f"   Output: {result.output[:200]}...")
                sys.exit(1)

        # Run the pipeline
        asyncio.run(run_pipeline())

    except (RuntimeError, ValueError, TypeError) as e:
        logger.exception("Pipeline execution failed")
        click.echo(f"❌ Pipeline execution failed: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def list_pipelines(_ctx: click.Context) -> None:
    """List available Meltano pipelines."""
    click.echo("📋 Listing available pipelines...")
    logger.info("Listing pipelines")

    try:
        # Create configuration and orchestrator
        config = create_gruponos_meltano_settings()
        orchestrator = create_gruponos_meltano_orchestrator(config)

        def list_available_pipelines() -> None:
            """List pipelines."""
            pipelines = orchestrator.list_pipelines()

            if pipelines:
                click.echo("Available pipelines:")
                for pipeline in pipelines:
                    click.echo(f"  - {pipeline}")
            else:
                click.echo("No pipelines found")

        # List pipelines
        list_available_pipelines()

    except (RuntimeError, ValueError, TypeError) as e:
        logger.exception("Failed to list pipelines")
        click.echo(f"❌ Failed to list pipelines: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--output-format",
    type=click.Choice(["json", "yaml", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def validate(_ctx: click.Context, *, output_format: str) -> None:
    """Validate configuration and pipeline setup."""
    if output_format != "json":
        click.echo("🔍 Running validation...")
        logger.info("Running validation with format: %s", output_format)

    try:
        # Create configuration
        config = create_gruponos_meltano_settings()

        # Run validation checks
        validation_results = {
            "configuration": "✅ Valid",
            "oracle_connection": "✅ Configured"
            if config.oracle and config.oracle.host
            else "❌ Missing",
            "meltano_project": "✅ Found"
            if config.meltano_project_root
            else "❌ Missing",
            "environment": config.environment,
            "debug_mode": config.is_debug_enabled(),
        }

        # Output results
        if output_format == "json":
            click.echo(json.dumps(validation_results, indent=2))
        elif output_format == "yaml":
            click.echo(yaml.dump(validation_results, default_flow_style=False))
        else:  # table
            click.echo("📋 Validation Results:")
            for component, status in validation_results.items():
                click.echo(f"  {component.ljust(20)}: {status}")

        if output_format != "json":
            logger.info("Validation completed successfully")

    except (RuntimeError, ValueError, TypeError) as e:
        logger.exception("Validation failed")
        click.echo(f"❌ Validation failed: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml"]),
    default="yaml",
    help="Configuration output format",
)
@click.option(
    "--show-secrets",
    is_flag=True,
    default=False,
    help="Include sensitive configuration (use with caution)",
)
@click.pass_context
def show_config(_ctx: click.Context, *, output_format: str, show_secrets: bool) -> None:
    """Show current configuration."""
    if output_format != "json":
        click.echo("📋 Current configuration:")
        logger.info("Showing configuration with format: %s", output_format)

    try:
        # Create configuration
        config: GruponosMeltanoSettings = create_gruponos_meltano_settings()

        # Build configuration dictionary
        oracle_config = None
        if config.oracle:
            oracle_config = {
                "host": config.oracle.host,
                "port": config.oracle.port,
                "service_name": config.oracle.service_name,
                "username": config.oracle.username,
                "password": "***HIDDEN***"
                if not show_secrets
                else config.oracle.password,
                "protocol": config.oracle.protocol,
            }

        wms_source_config = None
        if config.wms_source:
            wms_source_config = {
                "organization_id": config.wms_source.organization_id,
                "facility_code": config.wms_source.facility_code,
                "source_schema": config.wms_source.source_schema,
                "batch_size": config.wms_source.batch_size,
                "parallel_jobs": config.wms_source.parallel_jobs,
                "extract_mode": config.wms_source.extract_mode,
            }

        target_oracle_config = None
        if config.target_oracle:
            target_oracle_config = {
                "target_schema": config.target_oracle.target_schema,
                "table_prefix": config.target_oracle.table_prefix,
                "batch_size": config.target_oracle.batch_size,
                "parallel_workers": config.target_oracle.parallel_workers,
            }

        config_dict = {
            "app_name": config.app_name,
            "version": config.version,
            "environment": config.environment,
            "debug": config.debug,
            "log_level": config.log_level,
            "oracle": oracle_config,
            "wms_source": wms_source_config,
            "target_oracle": target_oracle_config,
            "job": {
                "job_name": getattr(config.job, "job_name", "gruponos-etl-pipeline"),
                "schedule": getattr(config.job, "schedule", "0 0 * * *"),
                "timeout_minutes": getattr(config.job, "timeout_minutes", 60),
                "retry_attempts": getattr(config.job, "retry_attempts", 3),
                "retry_delay_seconds": getattr(config.job, "retry_delay_seconds", 30),
            },
            "meltano": {
                "project_root": config.meltano_project_root,
                "environment": config.meltano_environment,
                "state_backend": config.meltano_state_backend,
            },
        }

        # Output configuration
        if output_format == "json":
            click.echo(json.dumps(config_dict, indent=2))
        else:  # yaml
            click.echo(yaml.dump(config_dict, default_flow_style=False))

        if output_format != "json":
            logger.info("Configuration displayed successfully")

    except (RuntimeError, ValueError, TypeError) as e:
        logger.exception("Failed to show configuration")
        click.echo(f"❌ Failed to show configuration: {e}")
        sys.exit(1)


@cli.command()
@click.argument("pipeline_name")
@click.option(
    "--max-retries",
    type=int,
    default=3,
    help="Maximum number of retry attempts",
)
@click.pass_context
def run_with_retry(
    _ctx: click.Context,
    pipeline_name: str,
    *,
    max_retries: int,
) -> None:
    """Run a pipeline with automatic retry logic.

    PIPELINE_NAME: Name of the pipeline to execute with retry
    """
    click.echo(f"🚀 Starting pipeline with retry: {pipeline_name}")
    click.echo(f"   Max retries: {max_retries}")
    logger.info(
        f"Starting pipeline with retry: {pipeline_name} (max retries: {max_retries})",
    )

    try:
        # Create configuration and orchestrator
        config = create_gruponos_meltano_settings()
        orchestrator = create_gruponos_meltano_orchestrator(config)

        # Create pipeline runner for retry functionality

        runner = create_gruponos_meltano_pipeline_runner(orchestrator.settings)

        async def run_with_retry_logic() -> None:
            """Run pipeline with retry logic."""
            result = await runner.run_with_retry(
                pipeline_name,
                max_retries=max_retries,
            )

            if result.success:
                click.echo("✅ Pipeline completed successfully after retries!")
                click.echo(f"   Job: {result.job_name}")
                click.echo(f"   Execution time: {result.execution_time:.2f}s")
                if result.output:
                    click.echo(f"   Output: {result.output[:200]}...")
            else:
                click.echo(
                    f"❌ Pipeline failed after retries: {result.error or 'Unknown error'}",
                )
                click.echo(f"   Job: {result.job_name}")
                click.echo(f"   Execution time: {result.execution_time:.2f}s")
                sys.exit(1)

        # Run with retry
        asyncio.run(run_with_retry_logic())

    except (RuntimeError, ValueError, TypeError) as e:
        logger.exception("Pipeline execution with retry failed")
        click.echo(f"❌ Pipeline execution failed: {e}")
        sys.exit(1)


# Entry point for CLI execution


if __name__ == "__main__":
    cli()
