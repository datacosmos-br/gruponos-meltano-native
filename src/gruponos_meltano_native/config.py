"""GrupoNOS Meltano Native Configuration using FLEXT Core.

This module centralizes all configuration using flext-core BaseConfig,
providing type safety, validation, and documentation.
"""

from __future__ import annotations

import os

from flext_core import BaseConfig, BaseSettings
from flext_observability.logging import get_logger
from pydantic import Field, ValidationInfo, field_validator

# Setup logger
logger = get_logger(__name__)


class OracleConnectionConfig(BaseConfig):
    """Oracle database connection configuration."""

    host: str = Field(..., description="Oracle database host")
    port: int = Field(default=1522, ge=1, le=65535, description="Oracle database port")
    service_name: str = Field(..., description="Oracle service name")
    username: str = Field(..., description="Oracle username")
    password: str = Field(..., description="Oracle password", repr=False)
    protocol: str = Field(
        default="tcps",
        pattern="^(tcp|tcps)$",
        description="Connection protocol",
    )
    ssl_server_dn_match: bool = Field(default=False, description="Verify SSL server DN")
    connection_timeout: int = Field(
        default=60,
        ge=1,
        description="Connection timeout in seconds",
    )
    retry_attempts: int = Field(default=3, ge=1, description="Number of retry attempts")
    retry_delay: int = Field(
        default=5,
        ge=1,
        description="Delay between retries in seconds",
    )

    # Performance settings
    batch_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Batch size for operations",
    )
    connection_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Connection pool size",
    )


class WMSSourceConfig(BaseConfig):
    """WMS Oracle source configuration."""

    # Inherit common Oracle settings
    oracle: OracleConnectionConfig

    # WMS specific settings
    api_enabled: bool = Field(
        default=False,
        description="Use WMS API instead of direct DB",
    )
    api_base_url: str | None = Field(default=None, description="WMS API base URL")
    api_username: str | None = Field(default=None, description="WMS API username")
    api_password: str | None = Field(
        default=None,
        description="WMS API password",
        repr=False,
    )

    # Extraction settings
    start_date: str | None = Field(
        default=None,
        description="Start date for incremental sync",
    )
    lookback_days: int = Field(
        default=7,
        ge=1,
        description="Lookback days for incremental sync",
    )

    @field_validator("api_base_url", "api_username", "api_password")
    @classmethod
    def validate_api_fields(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Validate API fields are provided if API is enabled."""
        if info.data.get("api_enabled") and not v:
            msg = f"{info.field_name} is required when api_enabled is True"
            raise ValueError(msg)
        return v


class TargetOracleConfig(BaseConfig):
    """Target Oracle database configuration."""

    # Inherit common Oracle settings
    oracle: OracleConnectionConfig

    # Target specific settings
    schema_name: str = Field(..., description="Target schema name")
    truncate_before_load: bool = Field(
        default=False,
        description="Truncate tables before loading",
    )
    analyze_after_load: bool = Field(
        default=True,
        description="Analyze tables after loading",
    )
    create_indexes: bool = Field(
        default=True,
        description="Create indexes after loading",
    )

    # Performance settings
    parallel_degree: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Oracle parallel degree",
    )
    commit_interval: int = Field(
        default=1000,
        ge=100,
        description="Commit interval for loads",
    )


class AlertConfig(BaseConfig):
    """Alert and monitoring configuration."""

    # Sync monitoring
    max_sync_duration_minutes: int = Field(
        default=60,
        ge=1,
        description="Max sync duration",
    )
    max_error_rate_percent: float = Field(
        default=5.0,
        ge=0,
        le=100,
        description="Max error rate %",
    )
    min_records_threshold: int = Field(
        default=100,
        ge=0,
        description="Min records threshold",
    )

    # Connection monitoring
    max_connection_time_seconds: float = Field(
        default=30.0,
        ge=1,
        description="Max connection time",
    )
    max_connection_failures: int = Field(
        default=3,
        ge=1,
        description="Max connection failures",
    )

    # System monitoring
    max_memory_usage_percent: float = Field(
        default=80.0,
        ge=0,
        le=100,
        description="Max memory %",
    )
    max_cpu_usage_percent: float = Field(
        default=85.0,
        ge=0,
        le=100,
        description="Max CPU %",
    )

    # Notification settings
    webhook_enabled: bool = Field(
        default=False,
        description="Enable webhook notifications",
    )
    webhook_url: str | None = Field(default=None, description="Webhook URL")
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    alert_email: str | None = Field(default=None, description="Alert email address")
    slack_enabled: bool = Field(default=False, description="Enable Slack notifications")
    slack_webhook: str | None = Field(default=None, description="Slack webhook URL")


class MeltanoConfig(BaseConfig):
    """Meltano-specific configuration."""

    project_id: str = Field(..., description="Meltano project ID")
    environment: str = Field(
        default="dev",
        pattern="^(dev|staging|production|prod)$",
        description="Environment",
    )
    state_backend: str = Field(
        default="file",
        pattern="^(file|s3|gcs|azure)$",
        description="State backend",
    )
    state_backend_uri: str | None = Field(default=None, description="State backend URI")

    # Logging
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    log_structured: bool = Field(default=True, description="Use structured logging")

    # Performance
    parallelism: int = Field(default=1, ge=1, le=10, description="Meltano parallelism")
    timeout_seconds: int = Field(default=3600, ge=60, description="Job timeout")


class GrupoNOSConfig(BaseSettings):
    """Main configuration for GrupoNOS Meltano Native.

    This configuration uses FLEXT Core BaseSettings which automatically:
    - Loads from environment variables
    - Validates all fields
    - Provides type safety
    - Generates documentation
    """

    # Sub-configurations (with defaults for initialization)
    wms_source: WMSSourceConfig | None = None
    target_oracle: TargetOracleConfig | None = None
    alerts: AlertConfig = Field(default_factory=AlertConfig)
    meltano: MeltanoConfig | None = None

    # Global settings
    project_name: str = Field(
        default="gruponos-meltano-native",
        description="Project name",
    )
    company: str = Field(default="GrupoNOS", description="Company name")
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    dry_run: bool = Field(default=False, description="Dry run mode")

    class Config:
        """Pydantic configuration."""

        env_prefix = "GRUPONOS_"
        env_nested_delimiter = "__"
        case_sensitive = False

    @classmethod
    def from_env(cls, _env_file: str | None = None) -> GrupoNOSConfig:
        """Create configuration from environment variables.

        Maps legacy environment variables to new structure.
        """
        # Map legacy and direct environment variables
        env_mapping = {
            # WMS Source Oracle - check both legacy and direct formats
            "GRUPONOS__WMS_SOURCE__ORACLE__HOST": os.getenv("GRUPONOS_WMS_HOST")
            or os.getenv("TAP_ORACLE_WMS_HOST"),
            "GRUPONOS__WMS_SOURCE__ORACLE__PORT": os.getenv("GRUPONOS_WMS_PORT")
            or os.getenv("TAP_ORACLE_WMS_PORT"),
            "GRUPONOS__WMS_SOURCE__ORACLE__SERVICE_NAME": os.getenv(
                "GRUPONOS_WMS_SERVICE_NAME",
            )
            or os.getenv(
                "TAP_ORACLE_WMS_SERVICE_NAME",
            ),
            "GRUPONOS__WMS_SOURCE__ORACLE__USERNAME": os.getenv("GRUPONOS_WMS_USERNAME")
            or os.getenv(
                "TAP_ORACLE_WMS_USERNAME",
            ),
            "GRUPONOS__WMS_SOURCE__ORACLE__PASSWORD": os.getenv("GRUPONOS_WMS_PASSWORD")
            or os.getenv(
                "TAP_ORACLE_WMS_PASSWORD",
            ),
            "GRUPONOS__WMS_SOURCE__ORACLE__BATCH_SIZE": os.getenv(
                "GRUPONOS_WMS_BATCH_SIZE",
            )
            or os.getenv(
                "TAP_ORACLE_WMS_BATCH_SIZE",
            ),
            # Target Oracle - check both legacy and direct formats
            "GRUPONOS__TARGET_ORACLE__ORACLE__HOST": os.getenv("GRUPONOS_TARGET_HOST")
            or os.getenv(
                "FLEXT_TARGET_ORACLE_HOST",
            ),
            "GRUPONOS__TARGET_ORACLE__ORACLE__PORT": os.getenv("GRUPONOS_TARGET_PORT")
            or os.getenv(
                "FLEXT_TARGET_ORACLE_PORT",
            ),
            "GRUPONOS__TARGET_ORACLE__ORACLE__SERVICE_NAME": os.getenv(
                "GRUPONOS_TARGET_SERVICE_NAME",
            )
            or os.getenv(
                "FLEXT_TARGET_ORACLE_SERVICE_NAME",
            ),
            "GRUPONOS__TARGET_ORACLE__ORACLE__USERNAME": os.getenv(
                "GRUPONOS_TARGET_USERNAME",
            )
            or os.getenv(
                "FLEXT_TARGET_ORACLE_USERNAME",
            ),
            "GRUPONOS__TARGET_ORACLE__ORACLE__PASSWORD": os.getenv(
                "GRUPONOS_TARGET_PASSWORD",
            )
            or os.getenv(
                "FLEXT_TARGET_ORACLE_PASSWORD",
            ),
            "GRUPONOS__TARGET_ORACLE__ORACLE__PROTOCOL": os.getenv(
                "GRUPONOS_TARGET_PROTOCOL",
            )
            or os.getenv(
                "FLEXT_TARGET_ORACLE_PROTOCOL",
            ),
            "GRUPONOS__TARGET_ORACLE__SCHEMA": os.getenv("GRUPONOS_TARGET_SCHEMA")
            or os.getenv("FLEXT_TARGET_ORACLE_SCHEMA"),
            # Meltano
            "GRUPONOS__MELTANO__PROJECT_ID": os.getenv("MELTANO_PROJECT_ID"),
            "GRUPONOS__MELTANO__ENVIRONMENT": os.getenv("MELTANO_ENVIRONMENT"),
            "GRUPONOS__MELTANO__LOG_LEVEL": os.getenv("MELTANO_LOG_LEVEL"),
            # Global
            "GRUPONOS__DEBUG_MODE": os.getenv("DEBUG"),
            "GRUPONOS__DRY_RUN": os.getenv("DRY_RUN"),
        }

        # Set mapped environment variables
        for key, value in env_mapping.items():
            if value is not None:
                os.environ[key] = str(value)

        # Create config from environment - need to build sub-configs
        try:
            # Build WMS source config if we have the minimum required fields
            wms_source = None
            if os.environ.get("GRUPONOS__WMS_SOURCE__ORACLE__HOST"):
                wms_oracle = OracleConnectionConfig(
                    host=os.environ["GRUPONOS__WMS_SOURCE__ORACLE__HOST"],
                    service_name=os.environ.get(
                        "GRUPONOS__WMS_SOURCE__ORACLE__SERVICE_NAME",
                        "WMS",
                    ),
                    username=os.environ.get(
                        "GRUPONOS__WMS_SOURCE__ORACLE__USERNAME",
                        "wms_user",
                    ),
                    password=os.environ.get(
                        "GRUPONOS__WMS_SOURCE__ORACLE__PASSWORD",
                        "",
                    ),
                    port=int(
                        os.environ.get("GRUPONOS__WMS_SOURCE__ORACLE__PORT", "1522"),
                    ),
                    batch_size=int(
                        os.environ.get(
                            "GRUPONOS__WMS_SOURCE__ORACLE__BATCH_SIZE",
                            "1000",
                        ),
                    ),
                )
                wms_source = WMSSourceConfig(oracle=wms_oracle)

            # Build target Oracle config if we have the minimum required fields
            target_oracle = None
            if os.environ.get("GRUPONOS__TARGET_ORACLE__ORACLE__HOST"):
                target_oracle_conn = OracleConnectionConfig(
                    host=os.environ["GRUPONOS__TARGET_ORACLE__ORACLE__HOST"],
                    service_name=os.environ.get(
                        "GRUPONOS__TARGET_ORACLE__ORACLE__SERVICE_NAME",
                        "TARGET",
                    ),
                    username=os.environ.get(
                        "GRUPONOS__TARGET_ORACLE__ORACLE__USERNAME",
                        "target_user",
                    ),
                    password=os.environ.get(
                        "GRUPONOS__TARGET_ORACLE__ORACLE__PASSWORD",
                        "",
                    ),
                    port=int(
                        os.environ.get("GRUPONOS__TARGET_ORACLE__ORACLE__PORT", "1522"),
                    ),
                    protocol=os.environ.get(
                        "GRUPONOS__TARGET_ORACLE__ORACLE__PROTOCOL",
                        "tcps",
                    ),
                )
                target_oracle = TargetOracleConfig(
                    oracle=target_oracle_conn,
                    schema_name=os.environ.get(
                        "GRUPONOS__TARGET_ORACLE__SCHEMA",
                        "WMS_SYNC",
                    ),
                )

            # Build Meltano config if we have the minimum required fields
            meltano = None
            if os.environ.get("GRUPONOS__MELTANO__PROJECT_ID"):
                meltano = MeltanoConfig(
                    project_id=os.environ["GRUPONOS__MELTANO__PROJECT_ID"],
                    environment=os.environ.get("GRUPONOS__MELTANO__ENVIRONMENT", "dev"),
                    log_level=os.environ.get("GRUPONOS__MELTANO__LOG_LEVEL", "INFO"),
                )

            # Create main config with sub-configs
            return cls(
                wms_source=wms_source,
                target_oracle=target_oracle,
                meltano=meltano,
                debug_mode=os.environ.get("GRUPONOS__DEBUG_MODE", "false").lower()
                == "true",
                dry_run=os.environ.get("GRUPONOS__DRY_RUN", "false").lower() == "true",
            )
        except (ValueError, KeyError, TypeError) as e:
            logger.warning("Could not load from environment, using defaults: %s", e)
            return cls(
                alerts=AlertConfig(),
            )

    def to_legacy_env(self) -> dict[str, str]:
        """Convert configuration back to legacy environment variables.

        Used for backward compatibility with existing scripts.
        """
        env_vars: dict[str, str] = {
            # Global
            "DEBUG": "true" if self.debug_mode else "false",
            "DRY_RUN": "true" if self.dry_run else "false",
        }

        # WMS Source - only if configured
        if self.wms_source is not None:
            env_vars.update(
                {
                    "TAP_ORACLE_WMS_HOST": self.wms_source.oracle.host,
                    "TAP_ORACLE_WMS_PORT": str(self.wms_source.oracle.port),
                    "TAP_ORACLE_WMS_SERVICE_NAME": self.wms_source.oracle.service_name,
                    "TAP_ORACLE_WMS_USERNAME": self.wms_source.oracle.username,
                    "TAP_ORACLE_WMS_PASSWORD": self.wms_source.oracle.password,
                    "TAP_ORACLE_WMS_BATCH_SIZE": str(self.wms_source.oracle.batch_size),
                },
            )

        # Target Oracle - only if configured
        if self.target_oracle is not None:
            env_vars.update(
                {
                    "FLEXT_TARGET_ORACLE_HOST": self.target_oracle.oracle.host,
                    "FLEXT_TARGET_ORACLE_PORT": str(self.target_oracle.oracle.port),
                    "FLEXT_TARGET_ORACLE_SERVICE_NAME": (
                        self.target_oracle.oracle.service_name
                    ),
                    "FLEXT_TARGET_ORACLE_USERNAME": self.target_oracle.oracle.username,
                    "FLEXT_TARGET_ORACLE_PASSWORD": self.target_oracle.oracle.password,
                    "FLEXT_TARGET_ORACLE_PROTOCOL": self.target_oracle.oracle.protocol,
                    "FLEXT_TARGET_ORACLE_SCHEMA": self.target_oracle.schema_name,
                },
            )

        # Meltano - only if configured
        if self.meltano is not None:
            env_vars.update(
                {
                    "MELTANO_PROJECT_ID": self.meltano.project_id,
                    "MELTANO_ENVIRONMENT": self.meltano.environment,
                    "MELTANO_LOG_LEVEL": self.meltano.log_level,
                },
            )

        return env_vars


# Singleton instance
_config: GrupoNOSConfig | None = None


def get_config() -> GrupoNOSConfig:
    """Get the configuration singleton."""
    # Use module-level configuration storage
    if "_config" not in globals() or globals()["_config"] is None:
        globals()["_config"] = GrupoNOSConfig.from_env()
    return globals()["_config"]


def reload_config() -> GrupoNOSConfig:
    """Reload configuration from environment."""
    # Use module-level configuration storage
    globals()["_config"] = GrupoNOSConfig.from_env()
    return globals()["_config"]
