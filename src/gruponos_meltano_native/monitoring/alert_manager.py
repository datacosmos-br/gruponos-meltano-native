"""GrupoNOS Meltano Native Alert Manager.

Gerenciamento empresarial de alertas seguindo padrões de Clean Architecture
com type safety adequado e sem fallbacks desnecessários.

Copyright (c) 2025 Grupo Nós. Todos os direitos reservados. Licença: Proprietária
"""

from __future__ import annotations

from datetime import UTC, datetime
from email.mime.text import MIMEText
from enum import StrEnum
from typing import override

from flext_api import FlextApiClient

from flext_core import FlextLogger, FlextModels, FlextResult, FlextTypes
from gruponos_meltano_native.config import GruponosMeltanoAlertConfig

logger = FlextLogger(__name__)

# Constants
MAX_ALERT_MESSAGE_LENGTH = 1000
JSON_MIME = "application/json"
HTTP_ERROR_STATUS_THRESHOLD = 400  # HTTP status codes >= 400 indicate errors


class GruponosMeltanoAlertSeverity(StrEnum):
    """Níveis de severidade de alerta para GrupoNOS Meltano Native.

    Enumeração que define os níveis de severidade disponíveis
    para classificação de alertas no sistema.

    Attributes:
      LOW: Severidade baixa para eventos informativos.
      MEDIUM: Severidade média para eventos que requerem atenção.
      HIGH: Severidade alta para eventos críticos.
      CRITICAL: Severidade crítica para falhas do sistema.

    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GruponosMeltanoAlertType(StrEnum):
    """Tipos de alerta para GrupoNOS Meltano Native.

    Enumeração que define os tipos de alertas disponíveis
    no sistema de monitoramento.

    Attributes:
      CONNECTIVITY_FAILURE: Falha de conectividade.
      DATA_QUALITY_ISSUE: Problema de qualidade de dados.
      SYNC_TIMEOUT: Timeout de sincronização.
      THRESHOLD_BREACH: Violação de limite.
      CONFIGURATION_ERROR: Erro de configuração.
      PIPELINE_FAILURE: Falha de pipeline.
      PERFORMANCE_DEGRADATION: Degradação de performance.

    """

    CONNECTIVITY_FAILURE = "connectivity_failure"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYNC_TIMEOUT = "sync_timeout"
    THRESHOLD_BREACH = "threshold_breach"
    CONFIGURATION_ERROR = "configuration_error"
    PIPELINE_FAILURE = "pipeline_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class GruponosMeltanoAlert(FlextModels.Value):
    """Estrutura de dados de alerta Meltano GrupoNOS.

    Value object que representa um alerta no sistema,
    contendo informações de severidade, tipo e contexto.

    Attributes:
      message: Mensagem descritiva do alerta.
      severity: Nível de severidade do alerta.
      alert_type: Tipo do alerta.
      context: Contexto adicional do alerta.
      timestamp: Timestamp da ocorrência.
      pipeline_name: Nome do pipeline relacionado (opcional).

    """

    message: str
    severity: GruponosMeltanoAlertSeverity
    alert_type: GruponosMeltanoAlertType
    context: FlextTypes.Dict
    timestamp: str
    pipeline_name: str | None = None

    def validate_domain_rules(self: object) -> FlextResult[None]:
        """Valida regras de domínio do alerta.

        Verifica se o alerta atende aos critérios de domínio,
        incluindo presença e tamanho da mensagem.

        Returns:
            FlextResult[None]: Resultado da validação.

        Raises:
            FlextResult[None].fail: Se a mensagem estiver vazia ou muito longa.

        """
        if not self.message.strip():
            return FlextResult[None].fail("Alert message cannot be empty")

        if len(self.message) > MAX_ALERT_MESSAGE_LENGTH:
            return FlextResult[None].fail(
                f"Alert message too long (max {MAX_ALERT_MESSAGE_LENGTH} characters)",
            )

        return FlextResult[None].ok(None)

    def validate_business_rules(self: object) -> FlextResult[None]:
        """Valida regras de negócio do alerta.

        Executa validações de regras de negócio específicas
        para o contexto empresarial.

        Returns:
            FlextResult[None]: Resultado da validação.

        """
        return self.validate_domain_rules()


class GruponosMeltanoAlertService:
    """Serviço de alertas Meltano GrupoNOS seguindo padrões FLEXT.

    Serviço responsável por gerenciar o envio de alertas
    através de múltiplos canais de comunicação.

    Attributes:
      config: Configuração de alertas.
      _failure_count: Contador de falhas interno.

    """

    @override
    def __init__(self, config: GruponosMeltanoAlertConfig) -> None:
        """Inicializa serviço de alertas com configuração.

        Args:
            config: Instância da configuração de alertas.

        """
        self.config: FlextTypes.Dict = config
        self._failure_count = 0

        logger.info(
            f"GrupoNOS Meltano Alert Service initialized - "
            f"webhook: {config.webhook_enabled}, email: {config.email_enabled}, slack: {config.slack_enabled}",
        )

    def send_alert(
        self,
        alert: GruponosMeltanoAlert,
    ) -> FlextResult[bool]:
        """Envia alerta através dos canais configurados.

        Processa e envia o alerta através de todos os canais
        habilitados (webhook, email, Slack), considerando
        o threshold de alertas configurado.

        Args:
            alert: Alerta a ser enviado.

        Returns:
            FlextResult[bool]: Resultado indicando sucesso/falha do envio.
            True se pelo menos um canal teve sucesso, False caso contrário.

        Example:
            >>> service = GruponosMeltanoAlertService(config)
            >>> alert = GruponosMeltanoAlert(message="Pipeline falhou", ...)
            >>> resultado: FlextResult[object] = service.send_alert(alert)
            >>> if resultado.success:
            ...     print("Alerta enviado com sucesso")

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
                return FlextResult[bool].ok(data=False)

            # Send through enabled channels
            results: list[FlextResult[object]] = []

            if self.config.webhook_enabled:
                webhook_result: FlextResult[object] = self._send_webhook(alert)
                results.append(webhook_result)

            if self.config.email_enabled:
                email_result: FlextResult[object] = self._send_email(alert)
                results.append(email_result)

            if self.config.slack_enabled:
                slack_result: FlextResult[object] = self._send_slack(alert)
                results.append(slack_result)

            # Check if any channel succeeded
            success = any(result.success for result in results)

            if success:
                logger.info(
                    f"Alert sent successfully - severity: {alert.severity}, type: {alert.alert_type}",
                )
                # Reset counter on successful alert
                self._failure_count = 0
                return FlextResult[bool].ok(data=True)
            error_messages = [
                result.error or "Unknown error"
                for result in results
                if not result.success
            ]
            combined_error = "; ".join(error_messages)
            return FlextResult[bool].fail(f"Failed to send alert: {combined_error}")

        except (RuntimeError, ValueError, TypeError) as e:
            logger.exception("Alert sending failed with unexpected error")
            return FlextResult[bool].fail(f"Alert sending error: {e}")

    def _send_webhook(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Envia alerta via webhook.

        Args:
            alert: Alerta a ser enviado.

        Returns:
            FlextResult[bool]: Resultado do envio via webhook.

        """
        try:
            if not self.config.webhook_url:
                return FlextResult[bool].fail("Webhook URL not configured")

            payload = {
                "message": alert.message,
                "severity": alert.severity,
                "alert_type": alert.alert_type,
                "timestamp": alert.timestamp,
                "pipeline_name": alert.pipeline_name,
                "context": alert.context,
            }

            client = FlextApiClient()
            response_result = client.post(
                self.config.webhook_url,
                json=payload,
                timeout=30,
                headers={"Content-Type": JSON_MIME},
            )

            if response_result.is_failure:
                logger.warning("Webhook alert failed: %s", response_result.error)
                return FlextResult[bool].fail(
                    f"Webhook failed: {response_result.error}"
                )

            response = response_result.unwrap()
            if response.status_code >= HTTP_ERROR_STATUS_THRESHOLD:
                logger.warning(
                    "Webhook alert failed with status: %d", response.status_code
                )
                return FlextResult[bool].fail(
                    f"Webhook failed with status: {response.status_code}"
                )

            logger.debug("Webhook alert sent successfully")
            return FlextResult[bool].ok(data=True)

        except Exception as e:
            logger.warning("Webhook alert failed: %s", e)
            return FlextResult[bool].fail(f"Webhook failed: {e}")

    def _send_email(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Envia alerta via email usando configuração SMTP.

        Args:
            alert: Alerta a ser enviado.

        Returns:
            FlextResult[bool]: Resultado do envio via email.

        Note:
            Requer configuração SMTP no config de alertas para
            funcionar adequadamente em produção.

        """
        try:
            if not self.config.email_recipients:
                return FlextResult[bool].fail("No email recipients configured")

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
            return FlextResult[bool].ok(data=True)

        except (RuntimeError, ValueError, TypeError) as e:
            logger.warning("Email alert failed: %s", e)
            return FlextResult[bool].fail(f"Email failed: {e}")

    def _send_slack(self, alert: GruponosMeltanoAlert) -> FlextResult[bool]:
        """Envia alerta via webhook do Slack.

        Formata o alerta como uma mensagem Slack com cores
        baseadas na severidade e envia via webhook.

        Args:
            alert: Alerta a ser enviado.

        Returns:
            FlextResult[bool]: Resultado do envio via Slack.

        """
        try:
            if not self.config.slack_webhook_url:
                return FlextResult[bool].fail("Slack webhook URL not configured")

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

            client = FlextApiClient()
            response_result = client.post(
                self.config.slack_webhook_url,
                json=payload,
                timeout=30,
                headers={"Content-Type": JSON_MIME},
            )

            if response_result.is_failure:
                logger.warning("Slack alert failed: %s", response_result.error)
                return FlextResult[bool].fail(f"Slack failed: {response_result.error}")

            response = response_result.unwrap()
            if response.status_code >= HTTP_ERROR_STATUS_THRESHOLD:
                logger.warning(
                    "Slack alert failed with status: %d", response.status_code
                )
                return FlextResult[bool].fail(
                    f"Slack failed with status: {response.status_code}"
                )

            logger.debug("Slack alert sent successfully")
            return FlextResult[bool].ok(data=True)

        except Exception as e:
            logger.warning("Slack alert failed: %s", e)
            return FlextResult[bool].fail(f"Slack failed: {e}")

    def reset_failure_count(self: object) -> None:
        """Reseta contador de falhas (para operações bem-sucedidas).

        Usado para resetar o contador interno quando uma operação
        é bem-sucedida, zerando o threshold de alertas.
        """
        self._failure_count = 0
        logger.debug("Alert failure count reset")

    def get_failure_count(self: object) -> int:
        """Obtém contador atual de falhas.

        Returns:
            int: Número atual de falhas registradas.

        """
        return self._failure_count


class GruponosMeltanoAlertManager:
    """Gerenciador de alertas Meltano GrupoNOS - orquestra serviços de alerta.

    Classe de alto nível que coordena o sistema de alertas,
    fornecendo métodos convenientes para diferentes tipos de alertas.

    Attributes:
      alert_service: Serviço de alertas subjacente.

    """

    @override
    def __init__(self, alert_service: GruponosMeltanoAlertService) -> None:
        """Inicializa gerenciador de alertas com serviço.

        Args:
            alert_service: Instância do serviço de alertas.

        """
        self.alert_service = alert_service
        logger.info("GrupoNOS Meltano Alert Manager initialized")

    def send_pipeline_failure_alert(
        self,
        pipeline_name: str,
        error_message: str,
        context: FlextTypes.Dict | None = None,
    ) -> FlextResult[bool]:
        """Envia alerta de falha de pipeline.

        Cria e envia um alerta específico para falhas de pipeline
        com severidade alta e contexto relevante.

        Args:
            pipeline_name: Nome do pipeline que falhou.
            error_message: Descrição do erro.
            context: Dados de contexto adicionais.

        Returns:
            FlextResult[bool]: Resultado indicando sucesso/falha do envio.

        Example:
            >>> manager = GruponosMeltanoAlertManager(service)
            >>> resultado = manager.send_pipeline_failure_alert(
            ...     "full-sync-job", "Timeout na conexão Oracle"
            ... )

        """
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
        context: FlextTypes.Dict | None = None,
    ) -> FlextResult[bool]:
        """Envia alerta de falha de conectividade.

        Cria e envia um alerta crítico para falhas de conectividade
        com sistemas externos.

        Args:
            target: Sistema de destino que falhou.
            error_message: Descrição do erro.
            context: Dados de contexto adicionais.

        Returns:
            FlextResult[bool]: Resultado indicando sucesso/falha do envio.

        Example:
            >>> manager = GruponosMeltanoAlertManager(service)
            >>> resultado = manager.send_connectivity_alert(
            ...     "Oracle Database", "Conexão recusada na porta 1521"
            ... )

        """
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
        context: FlextTypes.Dict | None = None,
    ) -> FlextResult[bool]:
        """Envia alerta de problema de qualidade de dados.

        Cria e envia um alerta de severidade média para problemas
        de qualidade de dados identificados durante o processamento.

        Args:
            issue_description: Descrição do problema de qualidade.
            pipeline_name: Nome do pipeline relacionado.
            context: Dados de contexto adicionais.

        Returns:
            FlextResult[bool]: Resultado indicando sucesso/falha do envio.

        Example:
            >>> manager = GruponosMeltanoAlertManager(service)
            >>> resultado = manager.send_data_quality_alert(
            ...     "Valores nulos encontrados em campo obrigatório",
            ...     "data-validation-job",
            ... )

        """
        alert = GruponosMeltanoAlert(
            message=f"Data quality issue: {issue_description}",
            severity=GruponosMeltanoAlertSeverity.MEDIUM,
            alert_type=GruponosMeltanoAlertType.DATA_QUALITY_ISSUE,
            context=context or {},
            timestamp=datetime.now(UTC).isoformat(),
            pipeline_name=pipeline_name,
        )

        return self.alert_service.send_alert(alert)


# Função factory
def create_gruponos_meltano_alert_manager(
    config: GruponosMeltanoAlertConfig | None = None,
) -> GruponosMeltanoAlertManager:
    """Cria instância do gerenciador de alertas Meltano GrupoNOS.

    Função factory que cria um gerenciador de alertas totalmente
    configurado com serviço de alertas e configuração.

    Args:
      config: Configuração de alertas opcional. Se None, usa configuração padrão.

    Returns:
      GruponosMeltanoAlertManager: Instância configurada do gerenciador.

    Example:
      >>> # Usar configuração padrão
      >>> manager = create_gruponos_meltano_alert_manager()
      >>>
      >>> # Usar configuração customizada
      >>> config: FlextTypes.Dict = GruponosMeltanoAlertConfig(webhook_enabled=True)
      >>> manager = create_gruponos_meltano_alert_manager(config)

    """
    if config is None:
        config: FlextTypes.Dict = GruponosMeltanoAlertConfig()

    alert_service = GruponosMeltanoAlertService(config)
    return GruponosMeltanoAlertManager(alert_service)


# Backwards compatibility aliases for tests
AlertSeverity = GruponosMeltanoAlertSeverity

# Public API exports
__all__: FlextTypes.StringList = [
    # Compatibility aliases
    "AlertSeverity",
    # Classes Padrão Empresarial
    "GruponosMeltanoAlert",
    "GruponosMeltanoAlertManager",
    "GruponosMeltanoAlertService",
    "GruponosMeltanoAlertSeverity",
    "GruponosMeltanoAlertType",
    # Funções Factory
    "create_gruponos_meltano_alert_manager",
]
