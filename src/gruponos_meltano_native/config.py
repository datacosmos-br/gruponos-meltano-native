"""GrupoNOS Meltano Native Configuration using FLEXT Core.

This module centralizes all configuration using flext-core BaseConfig,
providing type safety, validation, and documentation.
"""

from __future__ import annotations

from typing import Optional

from flext_core import BaseConfig, BaseSettings
from pydantic import Field, field_validator, model_validator


class OracleConnectionConfig(BaseConfig):
    """Oracle database connection configuration."""
    
    host: str = Field(..., description="Oracle database host")
    port: int = Field(1522, ge=1, le=65535, description="Oracle database port")
    service_name: str = Field(..., description="Oracle service name")
    username: str = Field(..., description="Oracle username")
    password: str = Field(..., description="Oracle password", repr=False)
    protocol: str = Field("tcps", pattern="^(tcp|tcps)$", description="Connection protocol")
    ssl_server_dn_match: bool = Field(False, description="Verify SSL server DN")
    connection_timeout: int = Field(60, ge=1, description="Connection timeout in seconds")
    retry_attempts: int = Field(3, ge=1, description="Number of retry attempts")
    retry_delay: int = Field(5, ge=1, description="Delay between retries in seconds")
    
    # Performance settings
    batch_size: int = Field(1000, ge=100, le=10000, description="Batch size for operations")
    connection_pool_size: int = Field(5, ge=1, le=20, description="Connection pool size")


class WMSSourceConfig(BaseConfig):
    """WMS Oracle source configuration."""
    
    # Inherit common Oracle settings
    oracle: OracleConnectionConfig
    
    # WMS specific settings
    api_enabled: bool = Field(False, description="Use WMS API instead of direct DB")
    api_base_url: Optional[str] = Field(None, description="WMS API base URL")
    api_username: Optional[str] = Field(None, description="WMS API username")
    api_password: Optional[str] = Field(None, description="WMS API password", repr=False)
    
    # Extraction settings
    start_date: Optional[str] = Field(None, description="Start date for incremental sync")
    lookback_days: int = Field(7, ge=1, description="Lookback days for incremental sync")
    
    @field_validator("api_base_url", "api_username", "api_password")
    @classmethod
    def validate_api_fields(cls, v, info):
        """Validate API fields are provided if API is enabled."""
        if info.data.get("api_enabled") and not v:
            raise ValueError(f"{info.field_name} is required when api_enabled is True")
        return v


class TargetOracleConfig(BaseConfig):
    """Target Oracle database configuration."""
    
    # Inherit common Oracle settings  
    oracle: OracleConnectionConfig
    
    # Target specific settings
    schema: str = Field(..., description="Target schema name")
    truncate_before_load: bool = Field(False, description="Truncate tables before loading")
    analyze_after_load: bool = Field(True, description="Analyze tables after loading")
    create_indexes: bool = Field(True, description="Create indexes after loading")
    
    # Performance settings
    parallel_degree: int = Field(4, ge=1, le=16, description="Oracle parallel degree")
    commit_interval: int = Field(1000, ge=100, description="Commit interval for loads")


class AlertConfig(BaseConfig):
    """Alert and monitoring configuration."""
    
    # Sync monitoring
    max_sync_duration_minutes: int = Field(60, ge=1, description="Max sync duration")
    max_error_rate_percent: float = Field(5.0, ge=0, le=100, description="Max error rate %")
    min_records_threshold: int = Field(100, ge=0, description="Min records threshold")
    
    # Connection monitoring
    max_connection_time_seconds: float = Field(30.0, ge=1, description="Max connection time")
    max_connection_failures: int = Field(3, ge=1, description="Max connection failures")
    
    # System monitoring  
    max_memory_usage_percent: float = Field(80.0, ge=0, le=100, description="Max memory %")
    max_cpu_usage_percent: float = Field(85.0, ge=0, le=100, description="Max CPU %")
    
    # Notification settings
    webhook_enabled: bool = Field(False, description="Enable webhook notifications")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    email_enabled: bool = Field(False, description="Enable email notifications")
    alert_email: Optional[str] = Field(None, description="Alert email address")
    slack_enabled: bool = Field(False, description="Enable Slack notifications")
    slack_webhook: Optional[str] = Field(None, description="Slack webhook URL")


class MeltanoConfig(BaseConfig):
    """Meltano-specific configuration."""
    
    project_id: str = Field(..., description="Meltano project ID")
    environment: str = Field("dev", pattern="^(dev|staging|prod)$", description="Environment")
    state_backend: str = Field("file", pattern="^(file|s3|gcs|azure)$", description="State backend")
    state_backend_uri: Optional[str] = Field(None, description="State backend URI")
    
    # Logging
    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    log_structured: bool = Field(True, description="Use structured logging")
    
    # Performance
    parallelism: int = Field(1, ge=1, le=10, description="Meltano parallelism")
    timeout_seconds: int = Field(3600, ge=60, description="Job timeout")


class GrupoNOSConfig(BaseSettings):
    """Main configuration for GrupoNOS Meltano Native.
    
    This configuration uses FLEXT Core BaseSettings which automatically:
    - Loads from environment variables
    - Validates all fields
    - Provides type safety
    - Generates documentation
    """
    
    # Sub-configurations
    wms_source: WMSSourceConfig
    target_oracle: TargetOracleConfig
    alerts: AlertConfig = Field(default_factory=AlertConfig)
    meltano: MeltanoConfig
    
    # Global settings
    project_name: str = Field("gruponos-meltano-native", description="Project name")
    company: str = Field("GrupoNOS", description="Company name")
    debug_mode: bool = Field(False, description="Enable debug mode")
    dry_run: bool = Field(False, description="Dry run mode")
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "GRUPONOS_"
        env_nested_delimiter = "__"
        case_sensitive = False
        
    @classmethod
    def from_env(cls) -> "GrupoNOSConfig":
        """Create configuration from environment variables.
        
        Maps legacy environment variables to new structure.
        """
        import os
        
        # Map legacy environment variables
        env_mapping = {
            # WMS Source Oracle
            "GRUPONOS__WMS_SOURCE__ORACLE__HOST": os.getenv("TAP_ORACLE_WMS_HOST"),
            "GRUPONOS__WMS_SOURCE__ORACLE__PORT": os.getenv("TAP_ORACLE_WMS_PORT"),
            "GRUPONOS__WMS_SOURCE__ORACLE__SERVICE_NAME": os.getenv("TAP_ORACLE_WMS_SERVICE_NAME"),
            "GRUPONOS__WMS_SOURCE__ORACLE__USERNAME": os.getenv("TAP_ORACLE_WMS_USERNAME"),
            "GRUPONOS__WMS_SOURCE__ORACLE__PASSWORD": os.getenv("TAP_ORACLE_WMS_PASSWORD"),
            "GRUPONOS__WMS_SOURCE__ORACLE__BATCH_SIZE": os.getenv("TAP_ORACLE_WMS_BATCH_SIZE"),
            
            # Target Oracle
            "GRUPONOS__TARGET_ORACLE__ORACLE__HOST": os.getenv("FLEXT_TARGET_ORACLE_HOST"),
            "GRUPONOS__TARGET_ORACLE__ORACLE__PORT": os.getenv("FLEXT_TARGET_ORACLE_PORT"),
            "GRUPONOS__TARGET_ORACLE__ORACLE__SERVICE_NAME": os.getenv("FLEXT_TARGET_ORACLE_SERVICE_NAME"),
            "GRUPONOS__TARGET_ORACLE__ORACLE__USERNAME": os.getenv("FLEXT_TARGET_ORACLE_USERNAME"),
            "GRUPONOS__TARGET_ORACLE__ORACLE__PASSWORD": os.getenv("FLEXT_TARGET_ORACLE_PASSWORD"),
            "GRUPONOS__TARGET_ORACLE__ORACLE__PROTOCOL": os.getenv("FLEXT_TARGET_ORACLE_PROTOCOL"),
            "GRUPONOS__TARGET_ORACLE__SCHEMA": os.getenv("FLEXT_TARGET_ORACLE_SCHEMA"),
            
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
        
        # Create config from environment
        return cls()
    
    def to_legacy_env(self) -> dict[str, str]:
        """Convert configuration back to legacy environment variables.
        
        Used for backward compatibility with existing scripts.
        """
        return {
            # WMS Source
            "TAP_ORACLE_WMS_HOST": self.wms_source.oracle.host,
            "TAP_ORACLE_WMS_PORT": str(self.wms_source.oracle.port),
            "TAP_ORACLE_WMS_SERVICE_NAME": self.wms_source.oracle.service_name,
            "TAP_ORACLE_WMS_USERNAME": self.wms_source.oracle.username,
            "TAP_ORACLE_WMS_PASSWORD": self.wms_source.oracle.password,
            "TAP_ORACLE_WMS_BATCH_SIZE": str(self.wms_source.oracle.batch_size),
            
            # Target Oracle
            "FLEXT_TARGET_ORACLE_HOST": self.target_oracle.oracle.host,
            "FLEXT_TARGET_ORACLE_PORT": str(self.target_oracle.oracle.port),
            "FLEXT_TARGET_ORACLE_SERVICE_NAME": self.target_oracle.oracle.service_name,
            "FLEXT_TARGET_ORACLE_USERNAME": self.target_oracle.oracle.username,
            "FLEXT_TARGET_ORACLE_PASSWORD": self.target_oracle.oracle.password,
            "FLEXT_TARGET_ORACLE_PROTOCOL": self.target_oracle.oracle.protocol,
            "FLEXT_TARGET_ORACLE_SCHEMA": self.target_oracle.schema,
            
            # Meltano
            "MELTANO_PROJECT_ID": self.meltano.project_id,
            "MELTANO_ENVIRONMENT": self.meltano.environment,
            "MELTANO_LOG_LEVEL": self.meltano.log_level,
            
            # Global
            "DEBUG": "true" if self.debug_mode else "false",
            "DRY_RUN": "true" if self.dry_run else "false",
        }


# Singleton instance
_config: Optional[GrupoNOSConfig] = None


def get_config() -> GrupoNOSConfig:
    """Get the configuration singleton."""
    global _config
    if _config is None:
        _config = GrupoNOSConfig.from_env()
    return _config


def reload_config() -> GrupoNOSConfig:
    """Reload configuration from environment."""
    global _config
    _config = GrupoNOSConfig.from_env()
    return _config