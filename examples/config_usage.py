#!/usr/bin/env python3
"""Example of using FLEXT Core configuration in GrupoNOS Meltano Native.

🚨 ARCHITECTURAL NOTE: This example file shows direct imports for demonstration
purposes. In production code within level 6 projects (specific implementations), these
dependencies should be injected via DI container instead of direct imports to maintain
Clean Architecture.

Example files are exempt from architectural constraints for educational purposes.
"""

# NOTE: Example files can show direct imports for educational purposes
# In production code, use DI container instead
from flext_core import get_logger

from gruponos_meltano_native.config import (
    GruponosMeltanoSettings,
    create_gruponos_meltano_settings,
)

logger = get_logger(__name__)


def demonstrate_config_usage() -> None:
    """Demonstrate various ways to use the configuration."""
    # Create configuration instance using real API
    config = create_gruponos_meltano_settings()

    logger.info("=== GrupoNOS Configuration Demo ===")

    # 1. Access basic configuration using real properties
    logger.info(
        "Application Configuration",
        app_name=config.app_name,
        version=config.version,
        environment=config.environment,
        project_name=config.project_name,
    )

    # 2. Access Meltano-specific settings using real properties
    logger.info(
        "Meltano Configuration",
        project_root=config.meltano_project_root,
        meltano_environment=config.meltano_environment,
        state_backend=config.meltano_state_backend,
    )

    # 3. Access logging configuration using real properties
    logger.info(
        "System Configuration",
        debug_mode=config.debug,
        log_level=config.log_level,
    )

    # 5. Show environment variable mapping (based on real config)
    logger.info(
        "Environment Variables",
        env_prefix="GRUPONOS_",
        example_vars=[
            "GRUPONOS_ENVIRONMENT",
            "GRUPONOS_PROJECT_NAME",
            "GRUPONOS_APP_NAME",
            "GRUPONOS_VERSION",
            "GRUPONOS_DEBUG",
        ],
    )

    # 6. Validate configuration
    try:
        # Configuration is already validated on load
        logger.info("✅ Configuration is valid")

        # You can also manually validate
        config.model_validate(config.model_dump())
        logger.info("✅ Manual validation passed")

    except (RuntimeError, ValueError, TypeError) as e:
        logger.exception("❌ Configuration validation failed", error=str(e))

    # 7. Export configuration as JSON
    config_json = config.model_dump_json(indent=2, exclude={"password", "api_password"})
    logger.info("Configuration (passwords excluded):", json_length=len(config_json))

    # 8. Create a modified configuration using real class
    modified_config_data = config.model_dump()
    modified_config_data["debug"] = True  # Use real field name
    modified_config_data["environment"] = "staging"  # Use real field name

    modified_config = GruponosMeltanoSettings.model_validate(modified_config_data)

    logger.info(
        "Modified configuration created",
        debug=modified_config.debug,
        env=modified_config.environment,
    )


def demonstrate_connection_manager_integration() -> None:
    """Show how configuration integrates with connection manager."""
    config = create_gruponos_meltano_settings()

    # Show how to create Oracle connection manager using real APIs
    logger.info(
        "Connection Manager Integration",
        project_root=config.meltano_project_root,
        environment=config.environment,
    )

    # Demonstrate how Oracle connection manager would be created
    # Using the real Oracle connection manager from the project
    try:
        from gruponos_meltano_native.oracle import (
            create_gruponos_meltano_oracle_connection_manager,
        )
        from gruponos_meltano_native.config import (
            GruponosMeltanoOracleConnectionConfig,
        )

        # Create a sample Oracle config
        oracle_config = GruponosMeltanoOracleConnectionConfig(
            host="localhost",
            port=1521,
            service_name="TESTDB",
            username="test",
            password="test",
        )

        # Create connection manager using real factory function
        connection_manager = create_gruponos_meltano_oracle_connection_manager(
            oracle_config
        )

        logger.info(
            "Oracle Connection Manager created successfully",
            manager_type=type(connection_manager).__name__,
        )

    except ImportError as e:
        logger.warning("Oracle connection manager not available", error=str(e))

    # Show production readiness
    if not config.debug:
        logger.info("Configuration ready for production use")
    else:
        logger.info("Configuration in debug mode for development")


if __name__ == "__main__":
    try:
        demonstrate_config_usage()
        logger.info("\n%s\n", "=" * 50)
        demonstrate_connection_manager_integration()
    except (RuntimeError, ValueError, TypeError, ImportError) as e:
        logger.exception("Demo failed", error=str(e))
