"""GrupoNOS Meltano Native Configuration - Settings using flext-core patterns.

Provides GrupoNOS-specific configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Self

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig, FlextResult


class GruponosMeltanoAlertConfig(FlextConfig):
    """GrupoNOS Meltano Alert Configuration extending FlextConfig."""

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_ALERT_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
    )

    # Alert configuration
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

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate alert configuration business rules."""
        try:
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

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Alert config validation failed: {e!s}")

    # Singleton pattern implementation (OLD pattern that works)
    _global_instance: ClassVar[GruponosMeltanoAlertConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using thread-safe pattern."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance


class GruponosMeltanoJobConfig(FlextConfig):
    """GrupoNOS Meltano Job Configuration extending FlextConfig."""

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_JOB_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
    )

    # Job configuration
    job_name: str = Field(
        default="gruponos-meltano-job",
        description="Name of the Meltano job",
    )

    schedule: str | None = Field(
        default=None,
        description="Cron schedule for the job",
    )

    timeout: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Job timeout in seconds",
    )

    retry_count: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retries on failure",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate job configuration business rules."""
        try:
            if not self.job_name.strip():
                return FlextResult[None].fail("Job name cannot be empty")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Job config validation failed: {e!s}")

    # Singleton pattern implementation (OLD pattern that works)
    _global_instance: ClassVar[GruponosMeltanoJobConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using thread-safe pattern."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance


class GruponosMeltanoOracleConnectionConfig(FlextConfig):
    """GrupoNOS Meltano Oracle Connection Configuration extending FlextConfig."""

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_ORACLE_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
    )

    # Oracle connection configuration
    host: str | None = Field(
        default=None,
        description="Oracle database host",
    )

    port: int = Field(
        default=1521,
        ge=1,
        le=65535,
        description="Oracle database port",
    )

    service_name: str | None = Field(
        default=None,
        description="Oracle database service name",
    )

    username: str | None = Field(
        default=None,
        description="Oracle database username",
    )

    password: SecretStr | None = Field(
        default=None,
        description="Oracle database password",
    )

    schema: str | None = Field(
        default=None,
        description="Oracle database default schema",
    )

    pool_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Connection pool size",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate Oracle connection configuration business rules."""
        try:
            if not self.host:
                return FlextResult[None].fail("Oracle host is required")

            if not self.service_name:
                return FlextResult[None].fail("Oracle service name is required")

            if not self.username:
                return FlextResult[None].fail("Oracle username is required")

            if not self.password:
                return FlextResult[None].fail("Oracle password is required")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                f"Oracle connection config validation failed: {e!s}"
            )

    # Singleton pattern implementation (OLD pattern that works)
    _global_instance: ClassVar[GruponosMeltanoOracleConnectionConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using thread-safe pattern."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance


class GruponosMeltanoTargetOracleConfig(FlextConfig):
    """GrupoNOS Meltano Target Oracle Configuration extending FlextConfig."""

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_TARGET_ORACLE_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
    )

    # Target Oracle configuration
    connection: GruponosMeltanoOracleConnectionConfig = Field(
        default_factory=GruponosMeltanoOracleConnectionConfig,
        description="Oracle connection configuration",
    )

    batch_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Batch size for loading data",
    )

    load_method: str = Field(
        default="upsert",
        description="Data loading method (insert, upsert, append)",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate target Oracle configuration business rules."""
        try:
            connection_validation = self.connection.validate_business_rules()
            if connection_validation.is_failure:
                return FlextResult[None].fail(
                    f"Connection validation failed: {connection_validation.error}"
                )

            valid_methods = {"insert", "upsert", "append"}
            if self.load_method not in valid_methods:
                return FlextResult[None].fail(
                    f"Load method must be one of {valid_methods}"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                f"Target Oracle config validation failed: {e!s}"
            )

    # Singleton pattern implementation (OLD pattern that works)
    _global_instance: ClassVar[GruponosMeltanoTargetOracleConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using thread-safe pattern."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance


class GruponosMeltanoWMSSourceConfig(FlextConfig):
    """GrupoNOS Meltano WMS Source Configuration extending FlextConfig."""

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_WMS_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
    )

    # WMS source configuration
    base_url: str | None = Field(
        default=None,
        description="Oracle WMS REST API base URL",
    )

    username: str | None = Field(
        default=None,
        description="Oracle WMS API username",
    )

    password: SecretStr | None = Field(
        default=None,
        description="Oracle WMS API password",
    )

    company_code: str | None = Field(
        default=None,
        description="Oracle WMS company code",
    )

    facility_code: str | None = Field(
        default=None,
        description="Oracle WMS facility code",
    )

    timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="API timeout in seconds",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate WMS source configuration business rules."""
        try:
            if not self.base_url:
                return FlextResult[None].fail("WMS base URL is required")

            if not self.username:
                return FlextResult[None].fail("WMS username is required")

            if not self.password:
                return FlextResult[None].fail("WMS password is required")

            if not self.company_code:
                return FlextResult[None].fail("WMS company code is required")

            if not self.facility_code:
                return FlextResult[None].fail("WMS facility code is required")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"WMS source config validation failed: {e!s}")

    # Singleton pattern implementation (OLD pattern that works)
    _global_instance: ClassVar[GruponosMeltanoWMSSourceConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using thread-safe pattern."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance


class GruponosMeltanoNativeConfig(FlextConfig):
    """GrupoNOS Meltano Native Configuration extending FlextConfig.

    Provides comprehensive configuration for GrupoNOS Oracle WMS integration
    and Meltano pipeline operations using Pydantic BaseSettings for validation
    and environment variable support with enhanced Pydantic 2.11 features.
    """

    model_config = SettingsConfigDict(
        env_prefix="GRUPONOS_MELTANO_NATIVE_",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
        # Enhanced Pydantic 2.11 features
        arbitrary_types_allowed=True,
        validate_return=True,
        serialize_by_alias=True,
        populate_by_name=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        str_strip_whitespace=True,
        defer_build=False,
        coerce_numbers_to_str=False,
        enable_decoding=True,
        # Custom encoders for complex types
        json_encoders={
            Path: str,
            datetime: lambda dt: dt.isoformat(),
        },
    )

    # Project identification
    project_name: str = Field(
        default="GrupoNOS Meltano Native",
        description="Name of the GrupoNOS Meltano Native project",
    )

    # Meltano configuration
    meltano_project_dir: str = Field(
        default=".",
        description="Meltano project directory",
    )

    meltano_environment: str = Field(
        default="dev",
        description="Meltano environment (dev, staging, prod)",
    )

    # Oracle WMS source configuration
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

    # Oracle target database configuration
    oracle_host: str | None = Field(
        default=None,
        description="Oracle database host",
    )

    oracle_port: int = Field(
        default=1521,
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

    # Pipeline configuration
    batch_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Batch size for data processing",
    )

    max_workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Maximum number of workers for parallel processing",
    )

    # Processing options
    enable_validation: bool = Field(
        default=True,
        description="Enable data validation",
    )

    dry_run: bool = Field(
        default=False,
        description="Enable dry run mode (no actual data changes)",
    )

    verbose: bool = Field(
        default=False,
        description="Enable verbose logging",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate GrupoNOS-specific business rules."""
        try:
            # Validate Oracle configuration completeness if any Oracle field is set
            oracle_fields = [
                self.oracle_host,
                self.oracle_service_name,
                self.oracle_username,
                self.oracle_password,
                self.oracle_schema,
            ]
            if any(oracle_fields) and not all(
                f
                for f in oracle_fields
                if f != self.oracle_password
                or (self.oracle_password and self.oracle_password.get_secret_value())
            ):
                return FlextResult[None].fail(
                    "All Oracle configuration fields must be provided if any are set"
                )

            # Validate WMS configuration completeness if any WMS field is set
            wms_fields = [
                self.wms_base_url,
                self.wms_username,
                self.wms_password,
                self.wms_company_code,
                self.wms_facility_code,
            ]
            if any(wms_fields) and not all(
                f
                for f in wms_fields
                if f != self.wms_password
                or (self.wms_password and self.wms_password.get_secret_value())
            ):
                return FlextResult[None].fail(
                    "All WMS configuration fields must be provided if any are set"
                )

            # Validate Meltano environment
            valid_environments = {"dev", "staging", "prod"}
            if self.meltano_environment not in valid_environments:
                return FlextResult[None].fail(
                    f"Meltano environment must be one of {valid_environments}"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Business rules validation failed: {e!s}")

    # Singleton pattern implementation (OLD pattern that works)
    _global_instance: ClassVar[GruponosMeltanoNativeConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using thread-safe pattern."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def create_for_development(cls, **overrides: object) -> Self:
        """Create configuration for development environment."""
        dev_overrides: dict[str, object] = {
            "meltano_environment": "dev",
            "verbose": True,
            "dry_run": True,
            "batch_size": 100,
            "max_workers": 2,
            **overrides,
        }
        return cls(**dev_overrides)

    @classmethod
    def create_for_production(cls, **overrides: object) -> Self:
        """Create configuration for production environment."""
        prod_overrides: dict[str, object] = {
            "meltano_environment": "prod",
            "verbose": False,
            "dry_run": False,
            "batch_size": 1000,
            "max_workers": 4,
            "enable_validation": True,
            **overrides,
        }
        return cls(**prod_overrides)

    @classmethod
    def create_for_testing(cls, **overrides: object) -> Self:
        """Create configuration for testing environment."""
        test_overrides: dict[str, object] = {
            "meltano_environment": "dev",
            "verbose": True,
            "dry_run": True,
            "batch_size": 10,
            "max_workers": 1,
            "enable_validation": True,
            **overrides,
        }
        return cls(**test_overrides)


def create_gruponos_meltano_settings(
    **overrides: object,
) -> GruponosMeltanoNativeConfig:
    """Create GrupoNOS Meltano Native settings with optional overrides.

    Factory function that creates a GruponosMeltanoNativeConfig instance
    with optional field overrides for customization.

    Args:
        **overrides: Optional field overrides for configuration.

    Returns:
        GruponosMeltanoNativeConfig: Configured instance.

    Example:
        >>> # Use default configuration
        >>> config = create_gruponos_meltano_settings()
        >>>
        >>> # Override specific fields
        >>> config = create_gruponos_meltano_settings(
        ...     meltano_environment="prod", batch_size=2000
        ... )

    """
    return GruponosMeltanoNativeConfig(**overrides)


# Export configuration classes
__all__: list[str] = [
    "GruponosMeltanoAlertConfig",
    "GruponosMeltanoJobConfig",
    "GruponosMeltanoNativeConfig",
    "GruponosMeltanoOracleConnectionConfig",
    "GruponosMeltanoTargetOracleConfig",
    "GruponosMeltanoWMSSourceConfig",
    "create_gruponos_meltano_settings",
]
