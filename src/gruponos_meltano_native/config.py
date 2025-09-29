"""GrupoNOS Meltano Native Configuration - Settings using flext-core patterns.

Provides GrupoNOS-specific configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

from pathlib import Path
from typing import Self, TypedDict

from pydantic import Field, SecretStr, computed_field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig, FlextResult, FlextTypes


class GruponosMeltanoNativeConfig(FlextConfig):
    """Single flat Config class for gruponos-meltano-native extending FlextConfig.

    Follows standardized FLEXT Config pattern:
    - Single flat class extending FlextConfig
    - Uses Pydantic 2 Settings with SettingsConfigDict
    - Uses SecretStr for sensitive data
    - Implements singleton pattern with inverse dependency injection
    - All fields with defaults from constants
    - Uses TypedDict structures for validation helpers
    """

    # TypedDict structures for configuration validation
    class AlertConfigDict(TypedDict):
        """Alert configuration dictionary structure."""

        webhook_enabled: bool
        webhook_url: str | None
        email_enabled: bool
        email_recipients: list[str]
        slack_enabled: bool
        slack_webhook_url: str | None
        alert_threshold: int

    class JobConfigDict(TypedDict):
        """Job configuration dictionary structure."""

        enabled: bool
        schedule: str | None
        timeout: int
        retries: int
        parallelism: int
        environment: str

    class OracleConnectionConfigDict(TypedDict):
        """Oracle connection configuration dictionary structure."""

        host: str | None
        port: int
        service_name: str | None
        username: str | None
        password: str | None  # Note: will be SecretStr in actual fields
        schema: str | None
        pool_size: int

    class TargetOracleConfigDict(TypedDict):
        """Target Oracle configuration dictionary structure."""

        batch_size: int
        load_method: str

    class WMSSourceConfigDict(TypedDict):
        """WMS source configuration dictionary structure."""

        base_url: str | None
        username: str | None
        password: str | None  # Note: will be SecretStr in actual fields
        company_code: str | None
        facility_code: str | None
        timeout: int

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_",
        case_sensitive=False,
        extra="allow",
        str_strip_whitespace=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        frozen=False,
        use_enum_values=True,
        validate_default=True,
        # Enhanced Pydantic 2.11+ features
        json_schema_extra={
            "title": "GrupoNOS Meltano Native Configuration",
            "description": "Enterprise Meltano native configuration extending FlextConfig",
        },
    )

    # Alert configuration fields
    webhook_enabled: bool = Field(
        default=False,
        description="Enable webhook alerts",
    )
    webhook_url: str | None = Field(
        default=None,
        description="Webhook URL for alerts",
    )
    email_enabled: bool = Field(
        default=False,
        description="Enable email alerts",
    )
    email_recipients: list[str] = Field(
        default_factory=list,
        description="Email recipients for alerts",
    )
    slack_enabled: bool = Field(
        default=False,
        description="Enable Slack alerts",
    )
    slack_webhook_url: str | None = Field(
        default=None,
        description="Slack webhook URL for alerts",
    )
    alert_threshold: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Alert threshold for failure count",
    )

    # Job configuration fields
    job_enabled: bool = Field(
        default=True,
        description="Enable job execution",
    )
    job_schedule: str | None = Field(
        default=None,
        description="Job schedule (cron format)",
    )
    job_timeout: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Job timeout in seconds",
    )
    job_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of job retries",
    )
    job_parallelism: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Job parallelism level",
    )
    job_environment: str = Field(
        default="production",
        description="Job execution environment",
    )

    # Oracle connection configuration fields
    oracle_host: str | None = Field(
        default=None,
        description="Oracle database host",
    )
    oracle_port: int = Field(
        default=1521,
        ge=1,
        le=65535,
        description="Oracle database port",
    )
    oracle_service_name: str | None = Field(
        default=None,
        description="Oracle database service name",
    )
    oracle_username: str | None = Field(
        default=None,
        description="Oracle database username",
    )
    oracle_password: SecretStr | None = Field(
        default=None,
        description="Oracle database password",
    )
    oracle_schema: str | None = Field(
        default=None,
        description="Oracle database default schema",
    )
    oracle_pool_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Oracle connection pool size",
    )

    # Target Oracle configuration fields
    target_batch_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Batch size for loading data",
    )
    target_load_method: str = Field(
        default="upsert",
        description="Data loading method (insert, upsert, append)",
    )

    # WMS source configuration fields
    wms_base_url: str | None = Field(
        default=None,
        description="Oracle WMS REST API base URL",
    )
    wms_username: str | None = Field(
        default=None,
        description="Oracle WMS API username",
    )
    wms_password: SecretStr | None = Field(
        default=None,
        description="Oracle WMS API password",
    )
    wms_company_code: str | None = Field(
        default=None,
        description="Oracle WMS company code",
    )
    wms_facility_code: str | None = Field(
        default=None,
        description="Oracle WMS facility code",
    )
    wms_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="WMS API timeout in seconds",
    )

    # Additional configuration fields
    project_name: str = Field(
        default="gruponos-meltano-native",
        description="Project name",
    )
    project_version: str = Field(
        default="0.9.0",
        description="Project version",
    )
    config_path: Path | None = Field(
        default=None,
        description="Configuration file path",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    # Field validators
    @field_validator("job_environment")
    @classmethod
    def validate_job_environment(cls, v: str) -> str:
        """Validate job environment."""
        valid_environments = {"development", "staging", "production"}
        if v.lower() not in valid_environments:
            msg = f"Invalid environment: {v}. Must be one of: {', '.join(sorted(valid_environments))}"
            raise ValueError(msg)
        return v.lower()

    @field_validator("target_load_method")
    @classmethod
    def validate_load_method(cls, v: str) -> str:
        """Validate load method."""
        valid_methods = {"insert", "upsert", "append"}
        if v not in valid_methods:
            msg = f"Load method must be one of {valid_methods}"
            raise ValueError(msg)
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        v_upper = v.upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v_upper not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of: {', '.join(valid_levels)}"
            raise ValueError(msg)
        return v_upper

    # Model validator
    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        """Validate complete configuration."""
        # Alert configuration validation
        if self.webhook_enabled and not self.webhook_url:
            msg = "Webhook URL required when webhook alerts enabled"
            raise ValueError(msg)

        if self.email_enabled and not self.email_recipients:
            msg = "Email recipients required when email alerts enabled"
            raise ValueError(msg)

        if self.slack_enabled and not self.slack_webhook_url:
            msg = "Slack webhook URL required when Slack alerts enabled"
            raise ValueError(msg)

        # Oracle connection validation
        if self.oracle_host and not self.oracle_service_name:
            msg = "Oracle service name is required when host is specified"
            raise ValueError(msg)

        if self.oracle_host and not self.oracle_username:
            msg = "Oracle username is required when host is specified"
            raise ValueError(msg)

        if self.oracle_host and not self.oracle_password:
            msg = "Oracle password is required when host is specified"
            raise ValueError(msg)

        # WMS source validation
        if self.wms_base_url and not self.wms_username:
            msg = "WMS username is required when base URL is specified"
            raise ValueError(msg)

        if self.wms_base_url and not self.wms_password:
            msg = "WMS password is required when base URL is specified"
            raise ValueError(msg)

        if self.wms_base_url and not self.wms_company_code:
            msg = "WMS company code is required when base URL is specified"
            raise ValueError(msg)

        if self.wms_base_url and not self.wms_facility_code:
            msg = "WMS facility code is required when base URL is specified"
            raise ValueError(msg)

        return self

    # Computed fields
    @computed_field
    @property
    def alert_config(self) -> AlertConfigDict:
        """Get alert configuration as dictionary."""
        return {
            "webhook_enabled": self.webhook_enabled,
            "webhook_url": self.webhook_url,
            "email_enabled": self.email_enabled,
            "email_recipients": self.email_recipients,
            "slack_enabled": self.slack_enabled,
            "slack_webhook_url": self.slack_webhook_url,
            "alert_threshold": self.alert_threshold,
        }

    @computed_field
    @property
    def job_config(self) -> JobConfigDict:
        """Get job configuration as dictionary."""
        return {
            "enabled": self.job_enabled,
            "schedule": self.job_schedule,
            "timeout": self.job_timeout,
            "retries": self.job_retries,
            "parallelism": self.job_parallelism,
            "environment": self.job_environment,
        }

    @computed_field
    @property
    def oracle_connection_config(self) -> OracleConnectionConfigDict:
        """Get Oracle connection configuration as dictionary."""
        return {
            "host": self.oracle_host,
            "port": self.oracle_port,
            "service_name": self.oracle_service_name,
            "username": self.oracle_username,
            "password": self.oracle_password.get_secret_value()
            if self.oracle_password
            else None,
            "schema": self.oracle_schema,
            "pool_size": self.oracle_pool_size,
        }

    @computed_field
    @property
    def target_oracle_config(self) -> TargetOracleConfigDict:
        """Get target Oracle configuration as dictionary."""
        return {
            "batch_size": self.target_batch_size,
            "load_method": self.target_load_method,
        }

    @computed_field
    @property
    def wms_source_config(self) -> WMSSourceConfigDict:
        """Get WMS source configuration as dictionary."""
        return {
            "base_url": self.wms_base_url,
            "username": self.wms_username,
            "password": self.wms_password.get_secret_value()
            if self.wms_password
            else None,
            "company_code": self.wms_company_code,
            "facility_code": self.wms_facility_code,
            "timeout": self.wms_timeout,
        }

    # Utility methods
    def get_oracle_password_value(self) -> str | None:
        """Get the actual Oracle password value (safely extract from SecretStr)."""
        if self.oracle_password is not None:
            return self.oracle_password.get_secret_value()
        return None

    def get_wms_password_value(self) -> str | None:
        """Get the actual WMS password value (safely extract from SecretStr)."""
        if self.wms_password is not None:
            return self.wms_password.get_secret_value()
        return None

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate configuration business rules."""
        try:
            # Alert configuration validation
            if self.webhook_enabled and not self.webhook_url:
                return FlextResult[None].fail(
                    "Webhook URL required when webhook alerts enabled"
                )

            if self.email_enabled and not self.email_recipients:
                return FlextResult[None].fail(
                    "Email recipients required when email alerts enabled"
                )

            if self.slack_enabled and not self.slack_webhook_url:
                return FlextResult[None].fail(
                    "Slack webhook URL required when Slack alerts enabled"
                )

            # Oracle connection validation
            if self.oracle_host:
                if not self.oracle_service_name:
                    return FlextResult[None].fail("Oracle service name is required")
                if not self.oracle_username:
                    return FlextResult[None].fail("Oracle username is required")
                if not self.oracle_password:
                    return FlextResult[None].fail("Oracle password is required")

            # WMS source validation
            if self.wms_base_url:
                if not self.wms_username:
                    return FlextResult[None].fail("WMS username is required")
                if not self.wms_password:
                    return FlextResult[None].fail("WMS password is required")
                if not self.wms_company_code:
                    return FlextResult[None].fail("WMS company code is required")
                if not self.wms_facility_code:
                    return FlextResult[None].fail("WMS facility code is required")

            # Target configuration validation
            valid_methods = {"insert", "upsert", "append"}
            if self.target_load_method not in valid_methods:
                return FlextResult[None].fail(
                    f"Load method must be one of {valid_methods}"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration validation failed: {e}")

    # Singleton pattern methods
    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using enhanced FlextConfig pattern."""
        return cls.get_or_create_shared_instance(project_name="gruponos-meltano-native")

    @classmethod
    def create_for_development(cls, **overrides: FlextTypes.Core.Value) -> Self:
        """Create configuration for development environment."""
        dev_overrides: dict[str, FlextTypes.Core.Value] = {
            "job_environment": "development",
            "job_timeout": 1800,  # 30 minutes for development
            "target_batch_size": 100,  # Smaller batches for development
            "wms_timeout": 60,  # Longer timeout for development
            "log_level": "DEBUG",
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="gruponos-meltano-native", **dev_overrides
        )

    @classmethod
    def create_for_production(cls, **overrides: FlextTypes.Core.Value) -> Self:
        """Create configuration for production environment."""
        prod_overrides: dict[str, FlextTypes.Core.Value] = {
            "job_environment": "production",
            "job_timeout": 3600,  # 1 hour for production
            "target_batch_size": 1000,  # Larger batches for production
            "wms_timeout": 30,  # Standard timeout for production
            "log_level": "INFO",
            "job_retries": 5,  # More retries for production
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="gruponos-meltano-native", **prod_overrides
        )

    @classmethod
    def create_for_testing(cls, **overrides: FlextTypes.Core.Value) -> Self:
        """Create configuration for testing environment."""
        test_overrides: dict[str, FlextTypes.Core.Value] = {
            "job_environment": "staging",
            "job_timeout": 600,  # 10 minutes for testing
            "target_batch_size": 10,  # Very small batches for testing
            "wms_timeout": 15,  # Short timeout for testing
            "log_level": "DEBUG",
            "job_retries": 1,  # Fewer retries for testing
            **overrides,
        }
        return cls.get_or_create_shared_instance(
            project_name="gruponos-meltano-native", **test_overrides
        )


def create_gruponos_meltano_settings(
    **overrides: FlextTypes.Core.Value,
) -> GruponosMeltanoNativeConfig:
    """Create GrupoNOS Meltano settings with optional overrides.

    Args:
        **overrides: Configuration field overrides

    Returns:
        GruponosMeltanoNativeConfig instance with applied overrides

    """
    return GruponosMeltanoNativeConfig.get_or_create_shared_instance(
        project_name="gruponos-meltano-native", **overrides
    )


# Backward compatibility aliases - all Config classes now use the single GruponosMeltanoNativeConfig
# These provide compatibility for existing code while directing to the standardized Config
GruponosMeltanoAlertConfig = GruponosMeltanoNativeConfig
GruponosMeltanoJobConfig = GruponosMeltanoNativeConfig
GruponosMeltanoOracleConnectionConfig = GruponosMeltanoNativeConfig
GruponosMeltanoTargetOracleConfig = GruponosMeltanoNativeConfig
GruponosMeltanoWMSSourceConfig = GruponosMeltanoNativeConfig


# Export configuration class (single class plus backward compatibility aliases)
__all__: FlextTypes.Core.StringList = [
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoNativeConfig",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoTargetOracleConfig",
    "GruponosMeltanoWMSSourceConfig",
    "create_gruponos_meltano_settings",
]
