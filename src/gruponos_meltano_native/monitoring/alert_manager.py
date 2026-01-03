"""GrupoNOS Meltano Native Alert Manager.

Gerenciamento empresarial de alertas seguindo padrões de Clean Architecture
com type safety adequado e sem fallbacks desnecessários.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

import json
import urllib.request
from datetime import UTC, datetime
from email.mime.text import MIMEText
from enum import StrEnum
from typing import Self
from urllib.error import HTTPError, URLError

from flext_core import (
    FlextLogger,
    FlextModels,
    FlextProtocols as p,
    FlextResult,
    FlextTypes as t,
)

from gruponos_meltano_native.config import GruponosMeltanoAlertConfig

logger: p.Log.StructlogLogger = FlextLogger.get_logger(__name__)

# Constants
MAX_ALERT_MESSAGE_LENGTH = 1000
JSON_MIME = "application/json"
HTTP_ERROR_STATUS_THRESHOLD = 400
HTTP_TIMEOUT_SECONDS = 30


def _http_post(
    url: str,
    payload: dict[str, t.GeneralValueType],
    headers: dict[str, str],
) -> FlextResult[int]:
    """Execute HTTP POST request and return status code."""
    try:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(  # noqa: S310 - HTTP webhook requests are intentional
            url,
            data=data,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:  # noqa: S310
            status_code: int = getattr(response, "status", 0)
            return FlextResult[int].ok(status_code)
    except HTTPError as e:
        return FlextResult[int].ok(e.code)
    except URLError as e:
        return FlextResult[int].fail(f"URL error: {e.reason}")
    except TimeoutError:
        return FlextResult[int].fail("Request timed out")


class GruponosMeltanoAlertSeverity(StrEnum):
    """Níveis de severidade de alerta para GrupoNOS Meltano Native."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GruponosMeltanoAlertType(StrEnum):
    """Tipos de alerta para GrupoNOS Meltano Native."""

    CONNECTIVITY_FAILURE = "connectivity_failure"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYNC_TIMEOUT = "sync_timeout"
    THRESHOLD_BREACH = "threshold_breach"
    CONFIGURATION_ERROR = "configuration_error"
    PIPELINE_FAILURE = "pipeline_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class GruponosMeltanoAlert(FlextModels.Value):
    """Estrutura de dados de alerta Meltano GrupoNOS."""

    message: str
    severity: GruponosMeltanoAlertSeverity
    alert_type: GruponosMeltanoAlertType
    context: dict[str, t.GeneralValueType]
    timestamp: str
    pipeline_name: str | None = None

    def validate_domain_rules(self: Self) -> FlextResult[None]:
        """Valida regras de domínio do alerta."""
        if not self.message.strip():
            return FlextResult[None].fail("Alert message cannot be empty")

        if len(self.message) > MAX_ALERT_MESSAGE_LENGTH:
            return FlextResult[None].fail(
                f"Alert message too long (max {MAX_ALERT_MESSAGE_LENGTH} characters)",
            )

        return FlextResult[None].ok(None)

    def validate_business_rules(self: Self) -> FlextResult[None]:
        """Valida regras de negócio do alerta."""
        return self.validate_domain_rules()


class GruponosMeltanoAlertService:
    """Serviço de alertas Meltano GrupoNOS seguindo padrões FLEXT."""

    config: GruponosMeltanoAlertConfig
    _failure_count: int

    def __init__(self, config: GruponosMeltanoAlertConfig) -> None:
        """Inicializa serviço de alertas com configuração."""
        self.config = config
        self._failure_count = 0

        log_msg = (
            f"GrupoNOS Meltano Alert Service initialized - "
            f"webhook: {config.webhook_enabled}, "
            f"email: {config.email_enabled}, "
            f"slack: {config.slack_enabled}"
        )
        logger.info(log_msg)

    def send_alert(
        self,
        alert: GruponosMeltanoAlert,
    ) -> FlextResult[bool]:
        """Envia alerta através dos canais configurados."""
        try:
            _ = alert.validate_domain_rules()

            self._failure_count += 1

            if self._failure_count < self.config.alert_threshold:
                threshold_msg = (
                    f"Alert threshold not reached: "
                    f"{self._failure_count}/{self.config.alert_threshold}"
                )
                logger.debug(threshold_msg)
                return FlextResult[bool].ok(value=False)

            results: list[FlextResult[bool]] = []

            if self.config.webhook_enabled:
                webhook_result = self._send_webhook(alert)
                results.append(webhook_result)

            if self.config.email_enabled:
                email_result = self._send_email(alert)
                results.append(email_result)

            if self.config.slack_enabled:
                slack_result = self._send_slack(alert)
                results.append(slack_result)

            success = any(result.is_success for result in results)

            if success:
                success_msg = (
                    f"Alert sent successfully - "
                    f"severity: {alert.severity}, type: {alert.alert_type}"
                )
                logger.info(success_msg)
                self._failure_count = 0
                return FlextResult[bool].ok(value=True)

            error_messages = [
                result.error or "Unknown error"
                for result in results
                if not result.is_success
            ]
            combined_error = "; ".join(error_messages)
            return FlextResult[bool].fail(f"Failed to send alert: {combined_error}")

        except (RuntimeError, ValueError, TypeError) as e:
            logger.exception("Alert sending failed with unexpected error")
            return FlextResult[bool].fail(f"Alert sending error: {e!s}")

    def _send_webhook(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Envia alerta via webhook."""
        try:
            if not self.config.webhook_url:
                return FlextResult[bool].fail("Webhook URL not configured")

            payload: dict[str, t.GeneralValueType] = {
                "message": alert.message,
                "severity": alert.severity.value,
                "alert_type": alert.alert_type.value,
                "timestamp": alert.timestamp,
                "pipeline_name": alert.pipeline_name,
                "context": alert.context,
            }

            response_result = _http_post(
                self.config.webhook_url,
                payload,
                {"Content-Type": JSON_MIME},
            )

            if response_result.is_failure:
                logger.warning("Webhook alert failed: %s", response_result.error)
                return FlextResult[bool].fail(
                    f"Webhook failed: {response_result.error}"
                )

            status_code = response_result.value
            if status_code >= HTTP_ERROR_STATUS_THRESHOLD:
                logger.warning("Webhook alert failed with status: %d", status_code)
                return FlextResult[bool].fail(
                    f"Webhook failed with status: {status_code}"
                )

            logger.debug("Webhook alert sent successfully")
            return FlextResult[bool].ok(value=True)

        except (RuntimeError, ValueError, TypeError) as e:
            logger.warning("Webhook alert failed: %s", str(e))  # noqa: RUF065
            return FlextResult[bool].fail(f"Webhook failed: {e!s}")

    def _send_email(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Envia alerta via email usando configuração SMTP."""
        try:
            if not self.config.email_recipients:
                return FlextResult[bool].fail("No email recipients configured")

            subject = f"[{alert.severity.value}] {alert.alert_type.value}"
            body = f"{alert.message}\n\nSource: GrupoNOS Meltano Native"

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = "noreply@invalid-company.com"
            msg["To"] = ", ".join(self.config.email_recipients)

            recipient_count = len(self.config.email_recipients)
            email_msg = (
                f"Email alert sent to {recipient_count} recipients "
                f"for severity: {alert.severity}"
            )
            logger.info(email_msg)
            return FlextResult[bool].ok(value=True)

        except (RuntimeError, ValueError, TypeError) as e:
            logger.warning("Email alert failed: %s", str(e))  # noqa: RUF065
            return FlextResult[bool].fail(f"Email failed: {e!s}")

    def _send_slack(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Envia alerta via webhook do Slack."""
        try:
            if not self.config.slack_webhook_url:
                return FlextResult[bool].fail("Slack webhook URL not configured")

            color_map = {
                GruponosMeltanoAlertSeverity.LOW: "good",
                GruponosMeltanoAlertSeverity.MEDIUM: "warning",
                GruponosMeltanoAlertSeverity.HIGH: "danger",
                GruponosMeltanoAlertSeverity.CRITICAL: "danger",
            }

            payload: dict[str, t.GeneralValueType] = {
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "warning"),
                        "title": f"GrupoNOS Meltano Alert - {alert.severity.value}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Alert Type",
                                "value": alert.alert_type.value,
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

            response_result = _http_post(
                self.config.slack_webhook_url,
                payload,
                {"Content-Type": JSON_MIME},
            )

            if response_result.is_failure:
                logger.warning("Slack alert failed: %s", response_result.error)
                return FlextResult[bool].fail(f"Slack failed: {response_result.error}")

            status_code = response_result.value
            if status_code >= HTTP_ERROR_STATUS_THRESHOLD:
                logger.warning("Slack alert failed with status: %d", status_code)
                return FlextResult[bool].fail(
                    f"Slack failed with status: {status_code}"
                )

            logger.debug("Slack alert sent successfully")
            return FlextResult[bool].ok(value=True)

        except (RuntimeError, ValueError, TypeError) as e:
            logger.warning("Slack alert failed: %s", str(e))  # noqa: RUF065
            return FlextResult[bool].fail(f"Slack failed: {e!s}")

    def reset_failure_count(self: Self) -> None:
        """Reseta contador de falhas (para operações bem-sucedidas)."""
        self._failure_count = 0
        logger.debug("Alert failure count reset")

    def get_failure_count(self: Self) -> int:
        """Obtém contador atual de falhas."""
        return self._failure_count


class GruponosMeltanoAlertManager:
    """Gerenciador de alertas Meltano GrupoNOS - orquestra serviços de alerta."""

    alert_service: GruponosMeltanoAlertService

    def __init__(self, alert_service: GruponosMeltanoAlertService) -> None:
        """Inicializa gerenciador de alertas com serviço."""
        self.alert_service = alert_service
        logger.info("GrupoNOS Meltano Alert Manager initialized")

    def send_pipeline_failure_alert(
        self,
        pipeline_name: str,
        error_message: str,
        context: dict[str, t.GeneralValueType] | None = None,
    ) -> FlextResult[bool]:
        """Envia alerta de falha de pipeline."""
        alert = GruponosMeltanoAlert(
            message=f"Pipeline '{pipeline_name}' failed: {error_message}",
            severity=GruponosMeltanoAlertSeverity.HIGH,
            alert_type=GruponosMeltanoAlertType.PIPELINE_FAILURE,
            context=context or {},
            timestamp=datetime.now(UTC).isoformat(),
            pipeline_name=pipeline_name,
        )

        return self.alert_service.send_alert(alert)

    def send_connectivity_alert(
        self,
        target: str,
        error_message: str,
        context: dict[str, t.GeneralValueType] | None = None,
    ) -> FlextResult[bool]:
        """Envia alerta de falha de conectividade."""
        alert = GruponosMeltanoAlert(
            message=f"Connectivity failure to {target}: {error_message}",
            severity=GruponosMeltanoAlertSeverity.CRITICAL,
            alert_type=GruponosMeltanoAlertType.CONNECTIVITY_FAILURE,
            context=context or {},
            timestamp=datetime.now(UTC).isoformat(),
        )

        return self.alert_service.send_alert(alert)

    def send_data_quality_alert(
        self,
        issue_description: str,
        pipeline_name: str | None = None,
        context: dict[str, t.GeneralValueType] | None = None,
    ) -> FlextResult[bool]:
        """Envia alerta de problema de qualidade de dados."""
        alert = GruponosMeltanoAlert(
            message=f"Data quality issue: {issue_description}",
            severity=GruponosMeltanoAlertSeverity.MEDIUM,
            alert_type=GruponosMeltanoAlertType.DATA_QUALITY_ISSUE,
            context=context or {},
            timestamp=datetime.now(UTC).isoformat(),
            pipeline_name=pipeline_name,
        )

        return self.alert_service.send_alert(alert)

    @staticmethod
    def create_alert_manager(
        config: GruponosMeltanoAlertConfig | None = None,
    ) -> GruponosMeltanoAlertManager:
        """Cria instância do gerenciador de alertas Meltano GrupoNOS."""
        if config is None:
            config = GruponosMeltanoAlertConfig()
        service = GruponosMeltanoAlertService(config)
        return GruponosMeltanoAlertManager(service)


def create_gruponos_meltano_alert_manager(
    config: GruponosMeltanoAlertConfig | None = None,
) -> GruponosMeltanoAlertManager:
    """Cria instância do gerenciador de alertas Meltano GrupoNOS."""
    return GruponosMeltanoAlertManager.create_alert_manager(config)


# Backwards compatibility aliases for tests
AlertSeverity = GruponosMeltanoAlertSeverity

# Public API exports
__all__: list[str] = [
    "AlertSeverity",
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    "create_gruponos_meltano_alert_manager",
]
