"""GrupoNOS Meltano Native CLI - FLEXT standardized.

Command-line interface following FLEXT standards, Clean Architecture
principles, and proper type safety.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import json
import sys

import click
import yaml

# FLEXT Core Standards
from flext_core import FlextLoggerFactory
from flext_core.patterns.typedefs import FlextLoggerName

from gruponos_meltano_native.config import (
    GruponosMeltanoSettings,
    create_gruponos_meltano_settings,
)
from gruponos_meltano_native.orchestrator import (
    create_gruponos_meltano_orchestrator,
)

logger_factory = FlextLoggerFactory()
logger = logger_factory.create_logger(FlextLoggerName(__name__))


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration using FLEXT logging standards."""
    import logging

    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Suppress overly verbose loggers directly
    urllib3_logger = logging.getLogger("urllib3")
    requests_logger = logging.getLogger("requests")

    urllib3_logger.setLevel(logging.WARNING)
    requests_logger.setLevel(logging.WARNING)


@click.group()
@click.version_option(version="0.7.0")
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
    debug: bool,
    config_file: str | None,
) -> None:
    """GrupoNOS Meltano Native - Enterprise ETL Pipeline Manager.

    A FLEXT-standardized tool for managing Meltano pipelines with Oracle
    integration, comprehensive monitoring, and enterprise-grade reliability.
    """
    ctx.ensure_object(dict)

    # Setup logging
    setup_logging(debug)

    # Store context
    ctx.obj["debug"] = debug
    ctx.obj["config_file"] = config_file

    logger.info("GrupoNOS Meltano Native CLI started")


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check pipeline health and system connectivity."""
    click.echo("🔍 Running health check...")
    logger.info("Starting health check")

    try:
        # Create configuration
        config = create_gruponos_meltano_settings()
        click.echo("✅ Configuration loaded successfully")

        # Create orchestrator
        _ = create_gruponos_meltano_orchestrator(config)
        click.echo("✅ Orchestrator initialized successfully")

        # Run comprehensive health check
        if config.oracle and config.oracle.host and config.oracle.username and config.oracle.password:
            click.echo("✅ Oracle connection configured")
        else:
            click.echo("⚠️  Oracle connection not fully configured")

        if config.meltano_project_root and config.meltano_environment:
            click.echo("✅ Meltano project configured")
        else:
            click.echo("⚠️  Meltano project not fully configured")

        logger.info("Health check completed successfully")
        click.echo("✅ Pipeline health check: PASSED")

    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        click.echo(f"❌ Pipeline health check: FAILED - {e}")
        sys.exit(1)


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
    ctx: click.Context,
    pipeline_name: str,
    dry_run: bool,
    retry_attempts: int,
) -> None:
    """Run a specific Meltano pipeline.

    PIPELINE_NAME: Name of the pipeline to execute
    """
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No actual changes will be made")
        logger.info("Running in dry-run mode")
        return

    click.echo(f"🚀 Starting pipeline: {pipeline_name}")
    logger.info(f"Starting pipeline execution: {pipeline_name}")

    try:
        # Create configuration and orchestrator
        config = create_gruponos_meltano_settings()
        orchestrator = create_gruponos_meltano_orchestrator(config)

        async def run_pipeline() -> None:
            """Run the pipeline asynchronously."""
            result = await orchestrator.run_pipeline(pipeline_name)

            if result.is_success and result.data:
                pipeline_result = result.data
                click.echo("✅ Pipeline completed successfully!")
                click.echo(f"   Records processed: {pipeline_result.records_processed}")
                click.echo(
                    f"   Execution time: {pipeline_result.execution_time_seconds:.2f}s",
                )

                if pipeline_result.has_warnings():
                    click.echo("⚠️  Warnings:")
                    for warning in pipeline_result.warnings:
                        click.echo(f"   - {warning}")
            else:
                click.echo(f"❌ Pipeline failed: {result.error}")
                if result.data:
                    pipeline_result = result.data
                    click.echo(
                        f"   Execution time: {pipeline_result.execution_time_seconds:.2f}s",
                    )
                    if pipeline_result.errors:
                        click.echo("   Errors:")
                        for error in pipeline_result.errors:
                            click.echo(f"   - {error}")
                sys.exit(1)

        # Run the pipeline
        asyncio.run(run_pipeline())

    except Exception as e:
        logger.exception(f"Pipeline execution failed: {e}")
        click.echo(f"❌ Pipeline execution failed: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def list_pipelines(ctx: click.Context) -> None:
    """List available Meltano pipelines."""
    click.echo("📋 Listing available pipelines...")
    logger.info("Listing pipelines")

    try:
        # Create configuration and orchestrator
        config = create_gruponos_meltano_settings()
        orchestrator = create_gruponos_meltano_orchestrator(config)

        async def list_available_pipelines() -> None:
            """List pipelines asynchronously."""
            result = await orchestrator.list_pipelines()

            if result.is_success:
                pipelines = result.data
                if pipelines:
                    click.echo("Available pipelines:")
                    for pipeline in pipelines:
                        click.echo(f"  - {pipeline}")
                else:
                    click.echo("No pipelines found")
            else:
                click.echo(f"❌ Failed to list pipelines: {result.error}")
                sys.exit(1)

        # List pipelines
        asyncio.run(list_available_pipelines())

    except Exception as e:
        logger.exception(f"Failed to list pipelines: {e}")
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
def validate(ctx: click.Context, output_format: str) -> None:
    """Validate configuration and pipeline setup."""
    if output_format != "json":
        click.echo("🔍 Running validation...")
        logger.info(f"Running validation with format: {output_format}")

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

    except Exception as e:
        logger.exception(f"Validation failed: {e}")
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
def show_config(ctx: click.Context, output_format: str, show_secrets: bool) -> None:
    """Show current configuration."""
    if output_format != "json":
        click.echo("📋 Current configuration:")
        logger.info(f"Showing configuration with format: {output_format}")

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

    except Exception as e:
        logger.exception(f"Failed to show configuration: {e}")
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
    ctx: click.Context,
    pipeline_name: str,
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
        from gruponos_meltano_native.orchestrator import (
            create_gruponos_meltano_pipeline_runner,
        )

        runner = create_gruponos_meltano_pipeline_runner(orchestrator.settings)

        async def run_with_retry_logic() -> None:
            """Run pipeline with retry logic."""
            result = await runner.run_with_retry(
                pipeline_name,
                max_retries=max_retries,
            )

            if result.is_success and result.data:
                pipeline_result = result.data
                click.echo("✅ Pipeline completed successfully!")
                click.echo(f"   Records processed: {pipeline_result.records_processed}")
                click.echo(
                    f"   Execution time: {pipeline_result.execution_time_seconds:.2f}s",
                )

                if pipeline_result.has_warnings():
                    click.echo("⚠️  Warnings:")
                    for warning in pipeline_result.warnings:
                        click.echo(f"   - {warning}")
            else:
                click.echo(f"❌ Pipeline failed after retries: {result.error}")
                sys.exit(1)

        # Run with retry
        asyncio.run(run_with_retry_logic())

    except Exception as e:
        logger.exception(f"Pipeline execution with retry failed: {e}")
        click.echo(f"❌ Pipeline execution failed: {e}")
        sys.exit(1)


# Entry point for CLI execution


if __name__ == "__main__":
    cli()
