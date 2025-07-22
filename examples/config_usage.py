#!/usr/bin/env python3
"""Example of using FLEXT Core configuration in GrupoNOS Meltano Native."""

from flext_core import LogLevel
from flext_observability.logging import LoggingConfig, get_logger, setup_logging

from gruponos_meltano_native.config import GrupoNOSConfig, get_config

# Setup logging
setup_logging(LoggingConfig(log_level=LogLevel.INFO))
logger = get_logger(__name__)


def demonstrate_config_usage() -> None:
    """Demonstrate various ways to use the configuration."""
    # Get configuration singleton
    config = get_config()

    logger.info("=== GrupoNOS Configuration Demo ===")

    # 1. Access nested configuration
    if config.wms_source is not None:
        logger.info(
            "WMS Source Database",
            host=config.wms_source.oracle.host,
            port=config.wms_source.oracle.port,
            service=config.wms_source.oracle.service_name,
            batch_size=config.wms_source.oracle.batch_size,
        )
    else:
        logger.info("WMS Source Database not configured")

    # 2. Access target configuration
    if config.target_oracle is not None:
        logger.info(
            "Target Oracle Database",
            host=config.target_oracle.oracle.host,
            schema=config.target_oracle.schema,
            parallel_degree=config.target_oracle.parallel_degree,
        )
    else:
        logger.info("Target Oracle Database not configured")

    # 3. Check alert configuration
    if config.alerts.webhook_enabled:
        logger.info(
            "Webhook alerts enabled",
            url=config.alerts.webhook_url,
            max_error_rate=config.alerts.max_error_rate_percent,
        )

    # 4. Environment-specific settings
    environment = "unknown"
    if config.meltano is not None:
        environment = config.meltano.environment

    logger.info(
        "Environment Configuration",
        environment=environment,
        debug_mode=config.debug_mode,
        dry_run=config.dry_run,
    )

    # 5. Convert to legacy environment variables (for backward compatibility)
    legacy_env = config.to_legacy_env()
    logger.info(
        "Legacy environment variables generated",
        count=len(legacy_env),
        sample_keys=list(legacy_env.keys())[:5],
    )

    # 6. Validate configuration
    try:
        # Configuration is already validated on load
        logger.info("✅ Configuration is valid")

        # You can also manually validate
        config.model_validate(config.model_dump())
        logger.info("✅ Manual validation passed")

    except Exception as e:
        logger.exception("❌ Configuration validation failed", error=str(e))

    # 7. Export configuration as JSON
    config_json = config.model_dump_json(indent=2, exclude={"password", "api_password"})
    logger.info("Configuration (passwords excluded):", json_length=len(config_json))

    # 8. Create a modified configuration
    modified_config_data = config.model_dump()
    modified_config_data["debug_mode"] = True
    if "meltano" in modified_config_data and modified_config_data["meltano"] is not None:
        modified_config_data["meltano"]["environment"] = "staging"

    modified_config = GrupoNOSConfig.model_validate(modified_config_data)

    modified_env = "unknown"
    if modified_config.meltano is not None:
        modified_env = modified_config.meltano.environment

    logger.info(
        "Modified configuration created",
        debug=modified_config.debug_mode,
        env=modified_env,
    )


def demonstrate_connection_manager_integration() -> None:
    """Show how configuration integrates with connection manager."""
    config = get_config()

    # Create connection manager from environment (the available pattern)
    # The OracleConnectionManager is created from environment variables
    # rather than from a separate config object

    # Access connection configuration safely
    target_host = "not configured"
    target_port = 0
    wms_host = "not configured"

    if config.target_oracle is not None:
        target_host = config.target_oracle.oracle.host
        target_port = config.target_oracle.oracle.port

    if config.wms_source is not None:
        wms_host = config.wms_source.oracle.host

    logger.info(
        "Connection manager configuration available",
        target_host=target_host,
        target_port=target_port,
        wms_host=wms_host,
    )

    # Note: Connection manager would be created from environment in actual usage
    # This example shows how configuration values are accessed
    if not config.dry_run:
        logger.info("Connection configuration ready for production use")
    else:
        logger.info("Connection test would be run in production mode")


if __name__ == "__main__":
    try:
        demonstrate_config_usage()
        logger.info("\n%s\n", "=" * 50)
        demonstrate_connection_manager_integration()
    except Exception as e:
        logger.exception("Demo failed", error=str(e))
