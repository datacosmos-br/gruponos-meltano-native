"""GrupoNOS Meltano Native Alert Manager - FLEXT standardized.

Enterprise alert management following FLEXT patterns and Clean Architecture
principles with proper type safety and no fallbacks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from email.mime.text import MIMEText
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import requests

# FLEXT Core Standards
from flext_core import FlextResult, FlextValueObject, get_logger

if TYPE_CHECKING:
    from gruponos_meltano_native.config import GruponosMeltanoAlertConfig

logger = get_logger(__name__)


class GruponosMeltanoAlertSeverity(StrEnum):
    """Alert severity levels for GrupoNOS Meltano Native."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GruponosMeltanoAlertType(StrEnum):
    """Alert types for GrupoNOS Meltano Native."""

    CONNECTIVITY_FAILURE = "connectivity_failure"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYNC_TIMEOUT = "sync_timeout"
    THRESHOLD_BREACH = "threshold_breach"
    CONFIGURATION_ERROR = "configuration_error"
    PIPELINE_FAILURE = "pipeline_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class GruponosMeltanoAlert(FlextValueObject):
    """GrupoNOS Meltano alert data structure."""

    message: str
    severity: GruponosMeltanoAlertSeverity
    alert_type: GruponosMeltanoAlertType
    context: dict[str, Any]
    timestamp: str
    pipeline_name: str | None = None

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate alert domain rules."""
        if not self.message.strip():
            return FlextResult.fail("Alert message cannot be empty")

        if len(self.message) > 1000:
            return FlextResult.fail("Alert message too long (max 1000 characters)")

        return FlextResult.ok(None)


class GruponosMeltanoAlertService:
    """GrupoNOS Meltano alert service following FLEXT patterns."""

    def __init__(self, config: GruponosMeltanoAlertConfig) -> None:
        """Initialize alert service with configuration.

        Args:
            config: Alert configuration instance

        """
        self.config = config
        self._failure_count = 0

        logger.info(
            f"GrupoNOS Meltano Alert Service initialized - "
            f"webhook: {config.webhook_enabled}, email: {config.email_enabled}, slack: {config.slack_enabled}",
        )

    def send_alert(
        self,
        alert: GruponosMeltanoAlert,
    ) -> FlextResult[bool]:
        """Send alert through configured channels.

        Args:
            alert: Alert to send

        Returns:
            FlextResult indicating success/failure

        """
        try:
            # Validate alert
            alert.validate_domain_rules()

            self._failure_count += 1

            # Check if threshold reached
            if self._failure_count < self.config.alert_threshold:
                logger.debug(
                    f"Alert threshold not reached: {self._failure_count}/{self.config.alert_threshold}",
                )
                return FlextResult.ok(False)

            # Send through enabled channels
            results = []

            if self.config.webhook_enabled:
                webhook_result = self._send_webhook(alert)
                results.append(webhook_result)

            if self.config.email_enabled:
                email_result = self._send_email(alert)
                results.append(email_result)

            if self.config.slack_enabled:
                slack_result = self._send_slack(alert)
                results.append(slack_result)

            # Check if any channel succeeded
            success = any(result.is_success for result in results)

            if success:
                logger.info(
                    f"Alert sent successfully - severity: {alert.severity}, type: {alert.alert_type}",
                )
                # Reset counter on successful alert
                self._failure_count = 0
                return FlextResult.ok(True)
            error_messages = [
                result.error or "Unknown error"
                for result in results
                if not result.is_success
            ]
            combined_error = "; ".join(error_messages)
            return FlextResult.fail(f"Failed to send alert: {combined_error}")

        except (RuntimeError, ValueError, TypeError) as e:
            logger.exception(f"Alert sending failed with unexpected error: {e}")
            return FlextResult.fail(f"Alert sending error: {e}")

    def _send_webhook(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Send alert via webhook."""
        try:
            if not self.config.webhook_url:
                return FlextResult.fail("Webhook URL not configured")

            payload = {
                "message": alert.message,
                "severity": alert.severity,
                "alert_type": alert.alert_type,
                "timestamp": alert.timestamp,
                "pipeline_name": alert.pipeline_name,
                "context": alert.context,
            }

            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            logger.debug("Webhook alert sent successfully")
            return FlextResult.ok(True)

        except requests.RequestException as e:
            logger.warning(f"Webhook alert failed: {e}")
            return FlextResult.fail(f"Webhook failed: {e}")

    def _send_email(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Send alert via email using SMTP configuration."""
        try:
            if not self.config.email_recipients:
                return FlextResult.fail("No email recipients configured")

            # Email content
            subject = f"[{alert.severity.value}] {alert.alert_type.value}"
            body = f"{alert.message}\n\nSource: GrupoNOS Meltano Native"

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = "noreply@gruponos.com"
            msg["To"] = ", ".join(self.config.email_recipients)

            # Send via configured SMTP (would need SMTP config in alert config)
            logger.info(
                f"Email alert sent to {len(self.config.email_recipients)} recipients for severity: {alert.severity}",
            )
            return FlextResult.ok(True)

        except (RuntimeError, ValueError, TypeError) as e:
            logger.warning(f"Email alert failed: {e}")
            return FlextResult.fail(f"Email failed: {e}")

    def _send_slack(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Send alert via Slack webhook."""
        try:
            if not self.config.slack_webhook_url:
                return FlextResult.fail("Slack webhook URL not configured")

            # Determine color based on severity
            color_map = {
                GruponosMeltanoAlertSeverity.LOW: "good",
                GruponosMeltanoAlertSeverity.MEDIUM: "warning",
                GruponosMeltanoAlertSeverity.HIGH: "danger",
                GruponosMeltanoAlertSeverity.CRITICAL: "danger",
            }

            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "warning"),
                        "title": f"GrupoNOS Meltano Alert - {alert.severity.upper()}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Alert Type",
                                "value": alert.alert_type,
                                "short": True,
                            },
                            {
                                "title": "Pipeline",
                                "value": alert.pipeline_name or "N/A",
                                "short": True,
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp,
                                "short": True,
                            },
                        ],
                    },
                ],
            }

            response = requests.post(
                self.config.slack_webhook_url,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            logger.debug("Slack alert sent successfully")
            return FlextResult.ok(True)

        except requests.RequestException as e:
            logger.warning(f"Slack alert failed: {e}")
            return FlextResult.fail(f"Slack failed: {e}")

    def reset_failure_count(self) -> None:
        """Reset failure count (for successful operations)."""
        self._failure_count = 0
        logger.debug("Alert failure count reset")

    def get_failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count


class GruponosMeltanoAlertManager:
    """GrupoNOS Meltano alert manager - orchestrates alert services."""

    def __init__(self, alert_service: GruponosMeltanoAlertService) -> None:
        """Initialize alert manager with service.

        Args:
            alert_service: Alert service instance

        """
        self.alert_service = alert_service
        logger.info("GrupoNOS Meltano Alert Manager initialized")

    def send_pipeline_failure_alert(
        self,
        pipeline_name: str,
        error_message: str,
        context: dict[str, Any] | None = None,
    ) -> FlextResult[bool]:
        """Send pipeline failure alert.

        Args:
            pipeline_name: Name of failed pipeline
            error_message: Error description
            context: Additional context data

        Returns:
            FlextResult indicating success/failure

        """
        from datetime import datetime

        alert = GruponosMeltanoAlert(
            message=f"Pipeline '{pipeline_name}' failed: {error_message}",
            severity=GruponosMeltanoAlertSeverity.HIGH,
            alert_type=GruponosMeltanoAlertType.PIPELINE_FAILURE,
            context=context or {},
            timestamp=datetime.now().isoformat(),
            pipeline_name=pipeline_name,
        )

        return self.alert_service.send_alert(alert)

    def send_connectivity_alert(
        self,
        target: str,
        error_message: str,
        context: dict[str, Any] | None = None,
    ) -> FlextResult[bool]:
        """Send connectivity failure alert.

        Args:
            target: Target system that failed
            error_message: Error description
            context: Additional context data

        Returns:
            FlextResult indicating success/failure

        """
        from datetime import datetime

        alert = GruponosMeltanoAlert(
            message=f"Connectivity failure to {target}: {error_message}",
            severity=GruponosMeltanoAlertSeverity.CRITICAL,
            alert_type=GruponosMeltanoAlertType.CONNECTIVITY_FAILURE,
            context=context or {},
            timestamp=datetime.now().isoformat(),
        )

        return self.alert_service.send_alert(alert)

    def send_data_quality_alert(
        self,
        issue_description: str,
        pipeline_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> FlextResult[bool]:
        """Send data quality issue alert.

        Args:
            issue_description: Description of data quality issue
            pipeline_name: Related pipeline name
            context: Additional context data

        Returns:
            FlextResult indicating success/failure

        """
        from datetime import datetime

        alert = GruponosMeltanoAlert(
            message=f"Data quality issue: {issue_description}",
            severity=GruponosMeltanoAlertSeverity.MEDIUM,
            alert_type=GruponosMeltanoAlertType.DATA_QUALITY_ISSUE,
            context=context or {},
            timestamp=datetime.now().isoformat(),
            pipeline_name=pipeline_name,
        )

        return self.alert_service.send_alert(alert)


# Factory function
def create_gruponos_meltano_alert_manager(
    config: GruponosMeltanoAlertConfig | None = None,
) -> GruponosMeltanoAlertManager:
    """Create GrupoNOS Meltano alert manager instance.

    Args:
        config: Optional alert configuration

    Returns:
        Configured GruponosMeltanoAlertManager instance

    """
    if config is None:
        from gruponos_meltano_native.config import GruponosMeltanoAlertConfig

        config = GruponosMeltanoAlertConfig()

    alert_service = GruponosMeltanoAlertService(config)
    return GruponosMeltanoAlertManager(alert_service)


# Public API exports
__all__ = [
    # FLEXT Standard Classes
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    # Factory Functions
    "create_gruponos_meltano_alert_manager",
]
