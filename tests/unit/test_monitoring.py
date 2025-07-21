"""Unit tests for monitoring functionality."""

from unittest.mock import Mock, patch

from flext_observability import AlertSeverity

from gruponos_meltano_native.config import AlertConfig
from gruponos_meltano_native.monitoring.alert_manager import (
    AlertManager,
    AlertService,
)


class TestMonitoring:
    """Test monitoring and alerting functionality."""

    def test_alert_config_defaults(self) -> None:
        """Test alert configuration defaults."""
        config = AlertConfig()

        assert config.max_sync_duration_minutes == 60
        assert config.max_error_rate_percent == 5.0
        assert config.min_records_threshold == 100
        assert config.max_connection_time_seconds == 30.0
        assert config.webhook_enabled is False
        assert config.email_enabled is False

    def test_alert_config_validation(self) -> None:
        """Test alert configuration validation."""
        # Valid config
        config = AlertConfig(
            max_sync_duration_minutes=120,
            max_error_rate_percent=10.0,
            webhook_enabled=True,
            webhook_url="https://hooks.slack.com/webhook",
        )

        assert config.max_sync_duration_minutes == 120
        assert config.max_error_rate_percent == 10.0
        assert config.webhook_enabled is True
        assert config.webhook_url == "https://hooks.slack.com/webhook"

    def test_alert_severity_enum(self) -> None:
        """Test AlertSeverity enum values."""
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"

    def test_alert_service_initialization(self) -> None:
        """Test AlertService initialization."""
        config = AlertConfig()
        service = AlertService(config)

        assert service.config == config
        assert hasattr(service, "send_alert")
        assert hasattr(service, "check_thresholds")

    def test_alert_manager_initialization(self) -> None:
        """Test AlertManager initialization."""
        config = AlertConfig()
        manager = AlertManager(config)

        assert manager.config == config
        assert hasattr(manager, "start_monitoring")
        assert hasattr(manager, "stop_monitoring")

    @patch("requests.post")
    def test_alert_service_webhook_notification(self, mock_post: Mock) -> None:
        """Test webhook notification functionality."""
        mock_post.return_value.status_code = 200

        config = AlertConfig(
            webhook_enabled=True,
            webhook_url="https://hooks.slack.com/test",
        )

        # Create alert manager with mocked alert service
        mock_alert_service = Mock(spec=AlertService)
        AlertManager(flext_alert_service=mock_alert_service)

        # Test sending alert - Use AlertService directly since that's what was tested in the initialization test
        service = AlertService(config)
        result = service.send_alert(
            message="Test alert",
            severity=AlertSeverity.MEDIUM,
        )

        # Should attempt to send webhook
        if config.webhook_enabled:
            mock_post.assert_called_once()
            assert result is True
        else:
            # Even without webhook, should return True for basic logging
            assert result is True

    def test_alert_manager_threshold_checking(self) -> None:
        """Test threshold checking functionality."""
        config = AlertConfig(
            max_error_rate_percent=5.0,
            min_records_threshold=100,
        )

        manager = AlertManager(config)

        # Test threshold violations
        test_metrics = {
            "error_rate": 10.0,  # Above threshold
            "records_processed": 50,  # Below threshold
        }

        violations = manager.check_thresholds(test_metrics)
        assert isinstance(violations, list)

    def test_alert_config_email_settings(self) -> None:
        """Test email alert configuration."""
        config = AlertConfig(
            email_enabled=True,
            alert_email="admin@example.com",
        )

        assert config.email_enabled is True
        assert config.alert_email == "admin@example.com"

    def test_alert_config_slack_settings(self) -> None:
        """Test Slack alert configuration."""
        config = AlertConfig(
            slack_enabled=True,
            slack_webhook="https://hooks.slack.com/services/T00/B00/XXX",
        )

        assert config.slack_enabled is True
        assert config.slack_webhook is not None

    def test_memory_cpu_thresholds(self) -> None:
        """Test memory and CPU threshold configuration."""
        config = AlertConfig(
            max_memory_usage_percent=90.0,
            max_cpu_usage_percent=95.0,
        )

        assert config.max_memory_usage_percent == 90.0
        assert config.max_cpu_usage_percent == 95.0
