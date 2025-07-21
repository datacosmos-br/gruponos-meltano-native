#!/usr/bin/env python3
"""Example of using FLEXT Core configuration in GrupoNOS Meltano Native."""

from flext_observability.logging import get_logger, setup_logging

from gruponos_meltano_native.config import GrupoNOSConfig, get_config
from gruponos_meltano_native.oracle.connection_manager import (
    OracleConnectionConfig,
    OracleConnectionManager,
)

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)


def demonstrate_config_usage() -> None:
    """Demonstrate various ways to use the configuration."""
    # Get configuration singleton
    config = get_config()

    logger.info("=== GrupoNOS Configuration Demo ===")

    # 1. Access nested configuration
    logger.info(
        "WMS Source Database",
        host=config.wms_source.oracle.host,
        port=config.wms_source.oracle.port,
        service=config.wms_source.oracle.service_name,
        batch_size=config.wms_source.oracle.batch_size,
    )

    # 2. Access target configuration
    logger.info(
        "Target Oracle Database",
        host=config.target_oracle.oracle.host,
        schema=config.target_oracle.schema,
        parallel_degree=config.target_oracle.parallel_degree,
    )

    # 3. Check alert configuration
    if config.alerts.webhook_enabled:
        logger.info(
            "Webhook alerts enabled",
            url=config.alerts.webhook_url,
            max_error_rate=config.alerts.max_error_rate_percent,
        )

    # 4. Environment-specific settings
    logger.info(
        "Environment Configuration",
        environment=config.meltano.environment,
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
    modified_config_data["meltano"]["environment"] = "staging"

    modified_config = GrupoNOSConfig.model_validate(modified_config_data)
    logger.info(
        "Modified configuration created",
        debug=modified_config.debug_mode,
        env=modified_config.meltano.environment,
    )


def demonstrate_connection_manager_integration() -> None:
    """Show how configuration integrates with connection manager."""
    config = get_config()

    # Create connection config from FLEXT config
    target_conn_config = OracleConnectionConfig(
        host=config.target_oracle.oracle.host,
        port=config.target_oracle.oracle.port,
        service_name=config.target_oracle.oracle.service_name,
        username=config.target_oracle.oracle.username,
        password=config.target_oracle.oracle.password,
        protocol=config.target_oracle.oracle.protocol,
        ssl_server_dn_match=config.target_oracle.oracle.ssl_server_dn_match,
        connection_timeout=config.target_oracle.oracle.connection_timeout,
        retry_attempts=config.target_oracle.oracle.retry_attempts,
        retry_delay=config.target_oracle.oracle.retry_delay,
    )

    # Create connection manager
    conn_manager = OracleConnectionManager(target_conn_config)

    logger.info(
        "Connection manager created from FLEXT config",
        host=target_conn_config.host,
        protocol=target_conn_config.protocol,
    )

    # Test connection if not in dry run mode
    if not config.dry_run:
        result = conn_manager.test_connection()
        if result["success"]:
            logger.info("✅ Connection test successful", details=result)
        else:
            logger.error("❌ Connection test failed", error=result["error"])
    else:
        logger.info("Skipping connection test in dry run mode")


if __name__ == "__main__":
    try:
        demonstrate_config_usage()
        logger.info("\n%s\n", "=" * 50)
        demonstrate_connection_manager_integration()
    except Exception as e:
        logger.exception("Demo failed", error=str(e))
