"""GrupoNOS Meltano Native Configuration - GRUPONOS specific implementation.

This module provides all GrupoNOS-specific configurations for Meltano integration
with Oracle WMS systems, built on FLEXT foundation patterns.
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextBaseSettings
from pydantic import Field, SecretStr

# =============================================
# GRUPONOS ORACLE WMS CONFIGURATION
# =============================================


class GruponosMeltanoOracleConnectionConfig(FlextBaseSettings):
    """Oracle WMS connection configuration for GrupoNOS."""

    host: str = Field(default="localhost", description="Oracle database host")
    port: int = Field(default=1521, description="Oracle database port")
    service_name: str | None = Field(default=None, description="Oracle service name")
    sid: str | None = Field(default=None, description="Oracle SID")
    username: str = Field(default="user", description="Database username")
    password: SecretStr = Field(default=SecretStr("password"), description="Database password")
    protocol: str = Field(default="TCP", description="Connection protocol")

    class Config:
        """Pydantic configuration for Oracle connection."""

        env_prefix = "FLEXT_TARGET_ORACLE_"
        extra = "ignore"


class GruponosMeltanoWMSSourceConfig(FlextBaseSettings):
    """Oracle WMS source configuration for GrupoNOS."""

    oracle: GruponosMeltanoOracleConnectionConfig | None = Field(default=None, description="Oracle connection config")
    api_enabled: bool = Field(default=True, description="Enable API access")
    api_base_url: str | None = Field(default=None, description="WMS API base URL")
    base_url: str = Field(default="https://example.com", description="WMS API base URL (legacy)")
    username: str = Field(default="user", description="WMS username")
    password: SecretStr = Field(default=SecretStr("password"), description="WMS password")
    company_code: str = Field(default="*", description="Company code")
    facility_code: str = Field(default="*", description="Facility code")
    entities: list[str] = Field(default=["allocation", "order_hdr", "order_dtl"], description="WMS entities to extract")
    organization_id: str = Field(default="*", description="Organization ID")
    source_schema: str = Field(default="WMS", description="Source schema name")
    batch_size: int = Field(default=1000, description="Processing batch size")
    parallel_jobs: int = Field(default=1, description="Number of parallel jobs")
    extract_mode: str = Field(default="incremental", description="Extract mode")
    page_size: int = Field(default=500, description="API page size")
    timeout: int = Field(default=600, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    enable_incremental: bool = Field(default=False, description="Enable incremental extraction")
    start_date: str = Field(default="2024-01-01T00:00:00Z", description="Start date for extraction")

    def model_post_init(self, /, __context: Any) -> None:
        """Post-init validation for WMS source configuration."""
        if self.api_enabled and not self.api_base_url:
            # Use base_url as fallback for api_base_url
            if self.base_url:
                # Set api_base_url to base_url if not provided
                object.__setattr__(self, "api_base_url", self.base_url)
            else:
                msg = "api_base_url is required when api_enabled is True"
                raise ValueError(msg)

    class Config:
        """Pydantic configuration for WMS source."""

        env_prefix = "TAP_ORACLE_WMS_"
        extra = "ignore"


class GruponosMeltanoTargetOracleConfig(FlextBaseSettings):
    """Oracle target configuration for GrupoNOS."""

    target_schema: str = Field(default="default", description="Target schema")
    table_prefix: str = Field(default="", description="Table prefix")
    parallel_workers: int = Field(default=1, description="Number of parallel workers")
    drop_target_tables: bool = Field(default=False, description="Drop target tables")
    enable_compression: bool = Field(default=True, description="Enable compression")
    batch_size: int = Field(default=5000, description="Batch size for loading")
    load_method: str = Field(default="append_only", description="Load method (append_only/upsert)")
    add_record_metadata: bool = Field(default=False, description="Add record metadata")

    class Config:
        """Pydantic configuration for Oracle target."""

        env_prefix = "FLEXT_TARGET_ORACLE_"
        extra = "ignore"


class GruponosMeltanoJobConfig(FlextBaseSettings):
    """Meltano job configuration for GrupoNOS."""

    job_name: str = Field(default="gruponos-etl-pipeline", description="Job name")
    extractor: str = Field(default="tap-oracle-wms", description="Extractor plugin name")
    loader: str = Field(default="target-oracle", description="Loader plugin name")
    schedule: str = Field(default="0 0 * * *", description="Job schedule (cron format)")
    transform: bool | None = Field(default=False, description="Enable DBT transformation")
    timeout_minutes: int = Field(default=60, description="Job timeout in minutes")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay_seconds: int = Field(default=30, description="Delay between retries in seconds")

    class Config:
        """Pydantic configuration for job settings."""

        env_prefix = "GRUPONOS_JOB_"
        extra = "ignore"


class GruponosMeltanoAlertConfig(FlextBaseSettings):
    """Alert configuration for GrupoNOS."""

    enabled: bool = Field(default=True, description="Enable alerts")
    email_recipients: list[str] = Field(default_factory=list, description="Email recipients")
    webhook_url: str | None = Field(default=None, description="Webhook URL for alerts")
    slack_webhook_url: str | None = Field(default=None, description="Slack webhook URL")
    webhook_enabled: bool = Field(default=False, description="Enable webhook alerts")
    email_enabled: bool = Field(default=False, description="Enable email alerts")
    slack_enabled: bool = Field(default=False, description="Enable Slack alerts")
    alert_threshold: int = Field(default=1, description="Number of failures before alerting")
    alert_on_failure: bool = Field(default=True, description="Alert on job failure")
    alert_on_success: bool = Field(default=False, description="Alert on job success")

    class Config:
        """Pydantic configuration for alert settings."""

        env_prefix = "GRUPONOS_ALERT_"
        extra = "ignore"


class GruponosMeltanoSettings(FlextBaseSettings):
    """Main GrupoNOS Meltano settings."""

    environment: str = Field(default="dev", description="Environment (dev/staging/prod)")
    project_name: str = Field(default="gruponos-meltano", description="Project name")
    app_name: str = Field(default="gruponos-meltano-native", description="Application name")
    version: str = Field(default="0.9.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")

    # Meltano Specific Settings
    meltano_project_root: str = Field(default=".", description="Meltano project root")
    meltano_environment: str = Field(default="dev", description="Meltano environment")
    meltano_state_backend: str = Field(default="systemdb", description="Meltano state backend")

    class Config:
        """Pydantic configuration for main settings."""

        env_prefix = "GRUPONOS_"
        extra = "ignore"  # Ignore extra environment variables

    @property
    def oracle_connection(self) -> GruponosMeltanoOracleConnectionConfig:
        """Get Oracle connection configuration."""
        return GruponosMeltanoOracleConnectionConfig()

    @property
    def oracle(self) -> GruponosMeltanoOracleConnectionConfig:
        """Get Oracle connection configuration (alias for compatibility)."""
        return self.oracle_connection

    @property
    def wms_source(self) -> GruponosMeltanoWMSSourceConfig:
        """Get WMS source configuration."""
        return GruponosMeltanoWMSSourceConfig()

    @property
    def target_oracle(self) -> GruponosMeltanoTargetOracleConfig:
        """Get Oracle target configuration."""
        return GruponosMeltanoTargetOracleConfig()

    @property
    def job_config(self) -> GruponosMeltanoJobConfig:
        """Get job configuration."""
        return GruponosMeltanoJobConfig()

    @property
    def alert_config(self) -> GruponosMeltanoAlertConfig:
        """Get alert configuration."""
        return GruponosMeltanoAlertConfig()

    @property
    def job(self) -> GruponosMeltanoJobConfig:
        """Get job configuration (alias for job_config)."""
        return self.job_config

    def get_oracle_connection_string(self) -> str:
        """Get Oracle connection string."""
        conn = self.oracle_connection
        if conn.service_name:
            return f"{conn.username}@{conn.host}:{conn.port}/{conn.service_name}"
        if conn.sid:
            return f"{conn.username}@{conn.host}:{conn.port}:{conn.sid}"
        return f"{conn.username}@{conn.host}:{conn.port}"

    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug

# =============================================
# FACTORY FUNCTIONS
# =============================================


def create_gruponos_meltano_settings() -> GruponosMeltanoSettings:
    """Create GrupoNOS Meltano settings instance."""
    return GruponosMeltanoSettings()


# Re-export for backward compatibility
__all__ = [
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoSettings",
    "GruponosMeltanoTargetOracleConfig",
    "GruponosMeltanoWMSSourceConfig",
    "create_gruponos_meltano_settings",
]
