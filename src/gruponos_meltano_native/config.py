"""GrupoNOS Meltano Native Configuration - GRUPONOS specific implementation.

This module provides all GrupoNOS-specific configurations for Meltano integration
with Oracle WMS systems, built on FLEXT foundation patterns.
"""

from __future__ import annotations

from typing import Optional

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
    password: SecretStr = Field(default="password", description="Database password")
    protocol: str = Field(default="TCP", description="Connection protocol")

    class Config:
        """Pydantic configuration for Oracle connection."""

        env_prefix = "FLEXT_TARGET_ORACLE_"
        extra = "ignore"

class GruponosMeltanoWMSSourceConfig(FlextBaseSettings):
    """Oracle WMS source configuration for GrupoNOS."""

    base_url: str = Field(default="https://example.com", description="WMS API base URL")
    username: str = Field(default="user", description="WMS username")
    password: SecretStr = Field(default="password", description="WMS password")
    company_code: str = Field(default="*", description="Company code")
    facility_code: str = Field(default="*", description="Facility code")
    entities: list[str] = Field(default=["allocation", "order_hdr", "order_dtl"], description="WMS entities to extract")
    page_size: int = Field(default=500, description="API page size")
    timeout: int = Field(default=600, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    enable_incremental: bool = Field(default=False, description="Enable incremental extraction")
    start_date: str = Field(default="2024-01-01T00:00:00Z", description="Start date for extraction")

    class Config:
        """Pydantic configuration for WMS source."""

        env_prefix = "TAP_ORACLE_WMS_"
        extra = "ignore"

class GruponosMeltanoTargetOracleConfig(FlextBaseSettings):
    """Oracle target configuration for GrupoNOS."""

    default_target_schema: str = Field(default="default", description="Default target schema")
    batch_size: int = Field(default=5000, description="Batch size for loading")
    load_method: str = Field(default="append_only", description="Load method (append_only/upsert)")
    add_record_metadata: bool = Field(default=False, description="Add record metadata")

    class Config:
        """Pydantic configuration for Oracle target."""

        env_prefix = "FLEXT_TARGET_ORACLE_"
        extra = "ignore"

class GruponosMeltanoJobConfig(FlextBaseSettings):
    """Meltano job configuration for GrupoNOS."""

    job_name: str = Field(default="default-job", description="Job name")
    extractor: str = Field(default="tap-oracle-wms", description="Extractor plugin name")
    loader: str = Field(default="target-oracle", description="Loader plugin name")
    schedule: str | None = Field(default=None, description="Job schedule (cron format)")
    transform: bool | None = Field(default=False, description="Enable DBT transformation")

    class Config:
        """Pydantic configuration for job settings."""

        env_prefix = "GRUPONOS_JOB_"
        extra = "ignore"

class GruponosMeltanoAlertConfig(FlextBaseSettings):
    """Alert configuration for GrupoNOS."""

    enabled: bool = Field(default=True, description="Enable alerts")
    email_recipients: list[str] = Field(default_factory=list, description="Email recipients")
    webhook_url: str | None = Field(default=None, description="Webhook URL for alerts")
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

    # Meltano Specific Settings
    meltano_project_root: str = Field(default=".", description="Meltano project root")
    meltano_environment: str = Field(default="dev", description="Meltano environment")

    class Config:
        """Pydantic configuration for main settings."""

        env_prefix = "GRUPONOS_"
        extra = "ignore"  # Ignore extra environment variables

    @property
    def oracle_connection(self) -> GruponosMeltanoOracleConnectionConfig:
        """Get Oracle connection configuration."""
        return GruponosMeltanoOracleConnectionConfig()

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
