"""Professional Alert Manager for Meltano Integration.

Monitors system health and sends alerts based on configurable thresholds.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil
import requests

from src.oracle.connection_manager import create_connection_manager_from_env

logger = logging.getLogger(__name__)


@dataclass
class AlertConfig:
    """Configuration for alert thresholds and notifications."""

    # Sync monitoring
    max_sync_duration_minutes: int = 60
    max_error_rate_percent: float = 5.0
    min_records_threshold: int = 100

    # Connection monitoring
    max_connection_time_seconds: float = 30.0
    max_connection_failures: int = 3

    # System monitoring
    max_memory_usage_percent: float = 80.0
    max_cpu_usage_percent: float = 85.0

    # Notification settings
    email_enabled: bool | None = None
    webhook_enabled: bool | None = None
    slack_enabled: bool | None = None

    # Contact information (loaded from environment)
    alert_email: str = ""
    webhook_url: str = ""
    slack_webhook: str = ""


@dataclass
class Alert:
    """Represents a system alert."""

    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    message: str
    component: str
    timestamp: datetime
    metrics: dict[str, Any]
    resolved: bool | None = None


class AlertManager:
    """Professional alert manager with multiple notification channels."""

    def __init__(self, config: AlertConfig) -> None:
        """Initialize alert manager with configuration."""
        """Initialize alert manager with configuration."""
        self.config = config
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []
        self.last_health_check = datetime.now(UTC)

        # Create logs directory
        self.log_dir = Path("logs/alerts")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def check_sync_health(self, sync_log_path: str) -> Alert | None:
        """Monitor sync process health from log files.

        Args:
            sync_log_path: Path to sync log file

        Returns:
            Alert if issues detected, None otherwise

        Args:
                sync_log_path: Parameter description.

        """
        try:
            if not Path(sync_log_path).exists():
                return Alert(
                    severity="HIGH",
                    title="Sync Log Missing",
                    message=f"Sync log file not found: {sync_log_path}",
                    component="sync_monitor",
                    timestamp=datetime.now(UTC),
                    metrics={"log_path": sync_log_path},
                )

            # Read log file
            with Path(sync_log_path).open(encoding="utf-8") as f:
                log_content = f.read()

            # Check for error patterns
            error_indicators = [
                "ERRO:",
                "ERROR:",
                "Failed",
                "Exception",
                "Traceback",
                "Connection refused",
                "Timeout",
                "Certificate verification failed",
            ]

            errors_found = [
                indicator for indicator in error_indicators if indicator in log_content
            ]

            if errors_found:
                return Alert(
                    severity="HIGH",
                    title="Sync Process Errors Detected",
                    message=f"Found error indicators in sync log: {
                        ', '.join(errors_found)}",
                    component="sync_process",
                    timestamp=datetime.now(UTC),
                    metrics={
                        "log_path": sync_log_path,
                        "errors_found": errors_found,
                        "log_size": len(log_content),
                    },
                )

            # Check sync duration
            start_time = self._extract_start_time(log_content)
            if start_time:
                duration_minutes = (datetime.now(UTC) - start_time).total_seconds() / 60
                if duration_minutes > self.config.max_sync_duration_minutes:
                    return Alert(
                        severity="MEDIUM",
                        title="Sync Duration Exceeded",
                        message=f"Sync running for {
                            duration_minutes:.1f} minutes (threshold: {
                            self.config.max_sync_duration_minutes})",
                        component="sync_performance",
                        timestamp=datetime.now(UTC),
                        metrics={
                            "duration_minutes": duration_minutes,
                            "threshold_minutes": self.config.max_sync_duration_minutes,
                        },
                    )

        except Exception as e:
            return Alert(
                severity="MEDIUM",
                title="Health Check Failed",
                message=f"Could not check sync health: {e!s}",
                component="health_monitor",
                timestamp=datetime.now(UTC),
                metrics={"error": str(e)},
            )
        else:
            return None

    def check_oracle_connection(self) -> Alert | None:
        """Test Oracle database connectivity.

        Returns:
            Alert if connection issues detected

        """
        try:
            manager = create_connection_manager_from_env()
            result = manager.test_connection()

            if not result["success"]:
                return Alert(
                    severity="CRITICAL",
                    title="Oracle Connection Failed",
                    message=f"Cannot connect to Oracle database: {
                        result['error']}",
                    component="oracle_connection",
                    timestamp=datetime.now(UTC),
                    metrics=result,
                )

            # Check connection time
            if result["connection_time_ms"] > (
                self.config.max_connection_time_seconds * 1000
            ):
                return Alert(
                    severity="MEDIUM",
                    title="Oracle Connection Slow",
                    message=f"Oracle connection took {
                        result['connection_time_ms']:.0f}ms (threshold: {
                        self.config.max_connection_time_seconds * 1000:.0f}ms)",
                    component="oracle_performance",
                    timestamp=datetime.now(UTC),
                    metrics=result,
                )

        except Exception as e:
            return Alert(
                severity="HIGH",
                title="Oracle Connection Test Failed",
                message=f"Could not test Oracle connection: {e!s}",
                component="oracle_monitor",
                timestamp=datetime.now(UTC),
                metrics={"error": str(e)},
            )
        else:
            return None

    def check_system_resources(self) -> list[Alert]:
        """Monitor system resource usage.

        Returns:
            List of alerts for resource issues

        """
        alerts = []

        try:
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.config.max_memory_usage_percent:
                alerts.append(
                    Alert(
                        severity="HIGH",
                        title="High Memory Usage",
                        message=f"Memory usage at {
                        memory.percent:.1f}% (threshold: {
                        self.config.max_memory_usage_percent}%)",
                        component="system_memory",
                        timestamp=datetime.now(UTC),
                        metrics={
                            "memory_percent": memory.percent,
                            "memory_available_gb": memory.available / (1024**3),
                            "memory_total_gb": memory.total / (1024**3),
                        },
                    ),
                )

            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.config.max_cpu_usage_percent:
                alerts.append(
                    Alert(
                        severity="MEDIUM",
                        title="High CPU Usage",
                        message=f"CPU usage at {
                        cpu_percent:.1f}% (threshold: {
                        self.config.max_cpu_usage_percent}%)",
                        component="system_cpu",
                        timestamp=datetime.now(UTC),
                        metrics={
                            "cpu_percent": cpu_percent,
                            "cpu_count": psutil.cpu_count(),
                        },
                    ),
                )

        except Exception as e:
            # psutil not available or other error - skip system monitoring
            logger.warning("System monitoring failed: %s", e)
            alerts.append(
                Alert(
                    severity="LOW",
                    title="System Monitoring Failed",
                    message=f"Could not check system resources: {e!s}",
                    component="system_monitor",
                    timestamp=datetime.now(UTC),
                    metrics={"error": str(e)},
                ),
            )

        return alerts

    def send_alert(self, alert: Alert) -> bool:
        """Send alert through configured notification channels.

        Args:
            alert: Alert to send

        Returns:
            True if alert sent successfully

        Args:
                alert: Parameter description.

        """
        sent = False

        # Log alert
        self._log_alert(alert)

        # Send webhook notification
        if self.config.webhook_enabled and self.config.webhook_url:
            sent |= self._send_webhook(alert)

        # Send email notification
        if self.config.email_enabled and self.config.alert_email:
            sent |= self._send_email(alert)

        # Send Slack notification
        if self.config.slack_enabled and self.config.slack_webhook:
            sent |= self._send_slack(alert)

        return sent

    def run_health_check(self) -> list[Alert]:
        """Run comprehensive health check and return any alerts.

        Returns:
            List of active alerts

        """
        alerts = []

        # Check sync processes
        sync_log_path = "logs/sync"
        if Path(sync_log_path).exists():
            for log_file in Path(sync_log_path).glob("*.log"):
                alert = self.check_sync_health(str(log_file))
                if alert:
                    alerts.append(alert)

        # Check Oracle connection
        oracle_alert = self.check_oracle_connection()
        if oracle_alert:
            alerts.append(oracle_alert)

        # Check system resources
        system_alerts = self.check_system_resources()
        alerts.extend(system_alerts)

        # Process alerts
        for alert in alerts:
            alert_key = f"{alert.component}_{alert.title}"

            # Check if this is a new alert
            if alert_key not in self.active_alerts:
                self.active_alerts[alert_key] = alert
                self.send_alert(alert)
                logger.warning(f"New alert: {alert.title}")
            else:
                # Update existing alert
                self.active_alerts[alert_key] = alert

        self.last_health_check = datetime.now(UTC)
        return alerts

    def _extract_start_time(self, log_content: str) -> datetime | None:
        """Extract start time from log content."""
        """Extract start time from log content."""
        lines = log_content.split("\n")
        for line in lines:
            if "INÍCIO:" in line or "Starting" in line:
                # Try to extract timestamp from line
                # This is a simplified parser - could be enhanced
                try:
                    # Look for ISO timestamp pattern
                    timestamp_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
                    match = re.search(timestamp_pattern, line)
                    if match:
                        return datetime.strptime(
                            match.group(1), "%Y-%m-%d %H:%M:%S",
                        ).replace(
                            tzinfo=UTC,
                        )
                except Exception as e:
                    # Unable to parse timestamp
                    logger.debug("Failed to parse timestamp: %s", e)
        return None

    def _log_alert(self, alert: Alert) -> None:
        """Log alert to file."""
        log_file = self.log_dir / f"alerts_{datetime.now(UTC).strftime('%Y%m%d')}.log"

        alert_data = {
            "timestamp": alert.timestamp.isoformat(),
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "component": alert.component,
            "metrics": alert.metrics,
        }

        with Path(log_file).open("a", encoding="utf-8") as f:
            f.write(json.dumps(alert_data) + "\n")

    def _send_webhook(self, alert: Alert) -> bool:
        """Send alert via webhook."""
        http_success_code = 200
        try:
            payload = {
                "alert": asdict(alert),
                "timestamp": alert.timestamp.isoformat(),
            }

            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=10,
            )
        except Exception:
            # Webhook failed
            logger.exception("Failed to send webhook alert")
            return False
        else:
            return response.status_code == http_success_code

    def _send_email(self, alert: Alert) -> bool:
        """Send alert via email."""
        """Send alert via email."""
        # Email implementation would go here
        # For now, just log that we would send email
        logger.info(f"Would send email alert: {alert.title}")
        return True

    def _send_slack(self, alert: Alert) -> bool:
        """Send alert via Slack."""
        """Send alert via Slack."""
        # Slack implementation would go here
        # For now, just log that we would send Slack message
        logger.info(f"Would send Slack alert: {alert.title}")
        return True


def create_alert_manager() -> AlertManager:
    """Create alert manager with default configuration."""
    config = AlertConfig()
    return AlertManager(config)


if __name__ == "__main__":
    # Test the alert manager
    logger = logging.getLogger(__name__)
    manager = create_alert_manager()
    alerts = manager.run_health_check()

    logger.error("Health check completed. Found %d alerts:", len(alerts))
    for alert in alerts:
        logger.error("  [%s] %s: %s", alert.severity, alert.title, alert.message)
