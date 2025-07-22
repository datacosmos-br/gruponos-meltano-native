"""Alert management for GrupoNOS pipeline monitoring.

Integrates with FLEXT observability patterns for structured alerting.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

import requests
import structlog
from flext_observability import AlertSeverity

from gruponos_meltano_native.config import AlertConfig

if TYPE_CHECKING:
    from flext_observability import AlertSeverity as AlertSeverityType
else:
    AlertSeverityType = AlertSeverity

logger = structlog.get_logger(__name__)


class AlertType(Enum):
    """Alert types for GrupoNOS pipeline."""

    CONNECTIVITY_FAILURE = "connectivity_failure"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYNC_TIMEOUT = "sync_timeout"
    THRESHOLD_BREACH = "threshold_breach"
    CONFIGURATION_ERROR = "configuration_error"


class AlertService:
    """Local AlertService wrapper for GrupoNOS project."""

    # Make AlertSeverity accessible as class attribute
    AlertSeverity = AlertSeverity

    def __init__(self, config: AlertConfig) -> None:
        """Initialize with AlertConfig."""
        self.config = config
        self.logger = logger.bind(component="alert_service")

    def send_alert(self, message: str, severity: AlertSeverityType, context: dict[str, Any] | None = None) -> bool:
        """Send alert using configuration."""
        log_data = {
            "message": message,
            "severity": severity.value,
            "webhook_enabled": self.config.webhook_enabled,
            "email_enabled": self.config.email_enabled,
        }
        if context:
            log_data.update(context)

        self.logger.info("Alert triggered", **log_data)

        success = True

        # Send webhook if enabled
        if self.config.webhook_enabled and self.config.webhook_url:
            try:
                response = requests.post(
                    self.config.webhook_url,
                    json={"text": f"{severity.value.upper()}: {message}"},
                    timeout=10,
                )
                success &= response.status_code == 200
            except (OSError, ValueError, RuntimeError) as e:
                self.logger.exception("Webhook notification failed", error=str(e))
                success = False

        return success

    def check_thresholds(self, metrics: dict[str, float]) -> list[str]:
        """Check if metrics violate thresholds."""
        violations = []

        error_rate = metrics.get("error_rate", 0.0)
        if error_rate > self.config.max_error_rate_percent:
            violations.append(
                f"Error rate {error_rate}% exceeds threshold "
                f"{self.config.max_error_rate_percent}%",
            )

        records_processed = metrics.get("records_processed", 0)
        if records_processed < self.config.min_records_threshold:
            violations.append(
                f"Records processed {records_processed} below threshold "
                f"{self.config.min_records_threshold}",
            )

        return violations


class AlertManager:
    """Alert management for GrupoNOS Meltano Native pipeline."""

    def __init__(
        self,
        config: AlertConfig | None = None,
        flext_alert_service: Any = None,
        flext_alerts: Any = None,
    ) -> None:
        """Initialize alert manager with configuration or FLEXT service."""
        if config is not None:
            self.config = config
            self.alert_service = AlertService(config)
        elif flext_alert_service is not None:
            # For backward compatibility with tests
            self.config = AlertConfig()  # Use defaults
            self.alert_service = flext_alert_service
        else:
            # Default config
            self.config = AlertConfig()
            self.alert_service = AlertService(self.config)

        # FLEXT alerts integration (optional)
        self.flext_alerts = flext_alerts
        self.logger = logger.bind(component="alert_manager")
        self._monitoring = False
        self._alert_count = 0

    def start_monitoring(self) -> None:
        """Start monitoring."""
        self._monitoring = True
        self.logger.info("Alert monitoring started")

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        self._monitoring = False
        self.logger.info("Alert monitoring stopped")

    @property
    def alert_count(self) -> int:
        """Get current alert count."""
        return self._alert_count

    def check_connection_time(self, connection_time: float) -> None:
        """Check if connection time exceeds threshold."""
        if hasattr(self.config, "max_connection_time_seconds") and connection_time > getattr(self.config, "max_connection_time_seconds", 30.0):
            self._alert_count += 1
            self.send_alert(
                AlertType.CONNECTIVITY_FAILURE,
                f"Connection time exceeded: {connection_time}s",
                AlertSeverity.HIGH,
            )

    def check_memory_usage(self, memory_percent: float) -> None:
        """Check if memory usage exceeds threshold."""
        if hasattr(self.config, "max_memory_usage_percent") and memory_percent > getattr(self.config, "max_memory_usage_percent", 90.0):
            self._alert_count += 1
            self.send_alert(
                AlertType.THRESHOLD_BREACH,
                f"Memory usage exceeded: {memory_percent}%",
                AlertSeverity.HIGH,
            )

    def check_cpu_usage(self, cpu_percent: float) -> None:
        """Check if CPU usage exceeds threshold."""
        if hasattr(self.config, "max_cpu_usage_percent") and cpu_percent > getattr(self.config, "max_cpu_usage_percent", 90.0):
            self._alert_count += 1
            self.send_alert(
                AlertType.THRESHOLD_BREACH,
                f"CPU usage exceeded: {cpu_percent}%",
                AlertSeverity.HIGH,
            )

    def check_sync_duration(self, duration_minutes: float) -> None:
        """Check if sync duration exceeds threshold."""
        if hasattr(self.config, "max_sync_duration_minutes") and duration_minutes > getattr(self.config, "max_sync_duration_minutes", 60.0):
            self._alert_count += 1
            self.send_alert(
                AlertType.SYNC_TIMEOUT,
                f"Sync duration exceeded: {duration_minutes} minutes",
                AlertSeverity.HIGH,
            )

    def check_thresholds(self, metrics: dict[str, float]) -> list[str]:
        """Check metrics against thresholds."""
        if hasattr(self.alert_service, "check_thresholds"):
            return self.alert_service.check_thresholds(metrics)
        return []  # Fallback for FLEXT AlertService

    def send_alert(
        self,
        alert_type: AlertType,
        message: str,
        level: AlertSeverityType = AlertSeverity.MEDIUM,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Send alert through FLEXT observability system."""
        alert_context = {
            "alert_type": alert_type.value,
            "pipeline": "gruponos-meltano-native",
            **(context or {}),
        }

        self.logger.warning(
            "Pipeline alert triggered",
            alert_type=alert_type.value,
            message=message,
            level=level.value,
            context=alert_context,
        )

        # Forward to FLEXT alert system if available
        if hasattr(self, "flext_alerts") and self.flext_alerts:
            self.flext_alerts.trigger_alert(
                title=f"GrupoNOS Pipeline: {alert_type.value}",
                message=message,
                severity=level,
                metadata=alert_context,
            )

    def connectivity_alert(self, service: str, error: str) -> None:
        """Alert for connectivity failures."""
        self.send_alert(
            AlertType.CONNECTIVITY_FAILURE,
            f"Failed to connect to {service}: {error}",
            level=AlertSeverity.HIGH,
            context={"service": service, "error": error},
        )

    def data_quality_alert(
        self,
        entity: str,
        issue: str,
        severity: str = "medium",
    ) -> None:
        """Alert for data quality issues."""
        level = AlertSeverity.HIGH if severity == "high" else AlertSeverity.MEDIUM
        self.send_alert(
            AlertType.DATA_QUALITY_ISSUE,
            f"Data quality issue in {entity}: {issue}",
            level=level,
            context={"entity": entity, "issue": issue, "severity": severity},
        )

    def sync_timeout_alert(self, entity: str, timeout_seconds: int) -> None:
        """Alert for sync timeouts."""
        self.send_alert(
            AlertType.SYNC_TIMEOUT,
            f"Sync timeout for {entity} after {timeout_seconds} seconds",
            level=AlertSeverity.HIGH,
            context={"entity": entity, "timeout_seconds": timeout_seconds},
        )
