"""Comprehensive alert manager tests targeting 100% coverage.

Tests alert service, alert manager, webhook functionality, and error handling.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

from flext_observability import AlertSeverity

from gruponos_meltano_native.config import AlertConfig
from gruponos_meltano_native.monitoring.alert_manager import (
    AlertManager,
    AlertService,
    AlertType,
)


class TestAlertServiceComprehensive:
    """Comprehensive test suite for AlertService class."""

    def test_alert_service_initialization(self) -> None:
        """Test AlertService initialization."""
        config = AlertConfig(
            webhook_enabled=True,
            webhook_url="http://test.com/webhook",
            email_enabled=False,
            max_error_rate_percent=5.0,
            min_records_threshold=100,
        )

        service = AlertService(config)
        assert service.config == config
        assert service.logger is not None

    def test_send_alert_webhook_success(self) -> None:
        """Test successful webhook alert sending."""
        config = AlertConfig(
            webhook_enabled=True,
            webhook_url="http://test.com/webhook",
        )
        service = AlertService(config)

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = service.send_alert("Test message", AlertSeverity.HIGH)

            assert result is True
            mock_post.assert_called_once_with(
                "http://test.com/webhook",
                json={"text": "HIGH: Test message"},
                timeout=10,
            )

    def test_send_alert_webhook_failure(self) -> None:
        """Test webhook alert sending failure (HTTP error)."""
        config = AlertConfig(
            webhook_enabled=True,
            webhook_url="http://test.com/webhook",
        )
        service = AlertService(config)

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response

            result = service.send_alert("Test message", AlertSeverity.HIGH)

            assert result is False

    def test_send_alert_webhook_exception_os_error(self) -> None:
        """Test webhook alert sending OSError exception."""
        config = AlertConfig(
            webhook_enabled=True,
            webhook_url="http://test.com/webhook",
        )
        service = AlertService(config)

        with patch("requests.post", side_effect=OSError("Network error")):
            result = service.send_alert("Test message", AlertSeverity.HIGH)
            assert result is False

    def test_send_alert_webhook_exception_value_error(self) -> None:
        """Test webhook alert sending ValueError exception."""
        config = AlertConfig(
            webhook_enabled=True,
            webhook_url="http://test.com/webhook",
        )
        service = AlertService(config)

        with patch("requests.post", side_effect=ValueError("Invalid JSON")):
            result = service.send_alert("Test message", AlertSeverity.HIGH)
            assert result is False

    def test_send_alert_webhook_exception_runtime_error(self) -> None:
        """Test webhook alert sending RuntimeError exception."""
        config = AlertConfig(
            webhook_enabled=True,
            webhook_url="http://test.com/webhook",
        )
        service = AlertService(config)

        with patch("requests.post", side_effect=RuntimeError("Runtime error")):
            result = service.send_alert("Test message", AlertSeverity.HIGH)
            assert result is False

    def test_send_alert_webhook_disabled(self) -> None:
        """Test alert sending when webhook is disabled."""
        config = AlertConfig(webhook_enabled=False)
        service = AlertService(config)

        result = service.send_alert("Test message", AlertSeverity.HIGH)
        assert result is True

    def test_send_alert_webhook_no_url(self) -> None:
        """Test alert sending when webhook URL is not set."""
        config = AlertConfig(webhook_enabled=True, webhook_url=None)
        service = AlertService(config)

        result = service.send_alert("Test message", AlertSeverity.HIGH)
        assert result is True

    def test_check_thresholds_error_rate_violation(self) -> None:
        """Test threshold checking for error rate violations."""
        config = AlertConfig(max_error_rate_percent=5.0, min_records_threshold=100)
        service = AlertService(config)

        metrics = {"error_rate": 10.0, "records_processed": 200}
        violations = service.check_thresholds(metrics)

        assert len(violations) == 1
        assert "Error rate 10.0% exceeds threshold 5.0%" in violations[0]

    def test_check_thresholds_records_violation(self) -> None:
        """Test threshold checking for records processed violations."""
        config = AlertConfig(max_error_rate_percent=5.0, min_records_threshold=100)
        service = AlertService(config)

        metrics = {"error_rate": 2.0, "records_processed": 50}
        violations = service.check_thresholds(metrics)

        assert len(violations) == 1
        assert "Records processed 50 below threshold 100" in violations[0]

    def test_check_thresholds_multiple_violations(self) -> None:
        """Test threshold checking with multiple violations."""
        config = AlertConfig(max_error_rate_percent=5.0, min_records_threshold=100)
        service = AlertService(config)

        metrics = {"error_rate": 10.0, "records_processed": 50}
        violations = service.check_thresholds(metrics)

        assert len(violations) == 2
        assert any("Error rate 10.0%" in v for v in violations)
        assert any("Records processed 50" in v for v in violations)

    def test_check_thresholds_no_violations(self) -> None:
        """Test threshold checking with no violations."""
        config = AlertConfig(max_error_rate_percent=5.0, min_records_threshold=100)
        service = AlertService(config)

        metrics = {"error_rate": 2.0, "records_processed": 200}
        violations = service.check_thresholds(metrics)

        assert len(violations) == 0

    def test_check_thresholds_missing_metrics(self) -> None:
        """Test threshold checking with missing metrics."""
        config = AlertConfig(max_error_rate_percent=5.0, min_records_threshold=100)
        service = AlertService(config)

        # Test with empty metrics
        violations = service.check_thresholds({})
        assert len(violations) == 1  # Only records_processed violation (default 0)

        # Test with partial metrics
        violations = service.check_thresholds({"error_rate": 2.0})
        assert len(violations) == 1  # Only records_processed violation


class TestAlertManagerComprehensive:
    """Comprehensive test suite for AlertManager class."""

    def test_alert_manager_init_with_config(self) -> None:
        """Test AlertManager initialization with config."""
        config = AlertConfig()
        manager = AlertManager(config=config)

        assert manager.config == config
        assert isinstance(manager.alert_service, AlertService)
        assert manager.flext_alerts is None
        assert not manager._monitoring

    def test_alert_manager_init_with_flext_service(self) -> None:
        """Test AlertManager initialization with FLEXT alert service."""
        mock_service = Mock()
        manager = AlertManager(flext_alert_service=mock_service)

        assert isinstance(manager.config, AlertConfig)
        assert manager.alert_service == mock_service
        assert manager.flext_alerts is None

    def test_alert_manager_init_with_flext_alerts(self) -> None:
        """Test AlertManager initialization with FLEXT alerts."""
        mock_alerts = Mock()
        manager = AlertManager(flext_alerts=mock_alerts)

        assert isinstance(manager.config, AlertConfig)
        assert isinstance(manager.alert_service, AlertService)
        assert manager.flext_alerts == mock_alerts

    def test_alert_manager_init_defaults(self) -> None:
        """Test AlertManager initialization with defaults."""
        manager = AlertManager()

        assert isinstance(manager.config, AlertConfig)
        assert isinstance(manager.alert_service, AlertService)
        assert manager.flext_alerts is None

    def test_start_stop_monitoring(self) -> None:
        """Test starting and stopping monitoring."""
        manager = AlertManager()

        assert not manager._monitoring

        manager.start_monitoring()
        assert manager._monitoring

        manager.stop_monitoring()
        assert not manager._monitoring

    def test_check_thresholds_with_service_method(self) -> None:
        """Test check_thresholds when alert_service has method."""
        config = AlertConfig(max_error_rate_percent=5.0)
        manager = AlertManager(config=config)

        metrics = {"error_rate": 10.0}
        violations = manager.check_thresholds(metrics)

        assert len(violations) >= 1
        assert any("Error rate" in v for v in violations)

    def test_check_thresholds_fallback(self) -> None:
        """Test check_thresholds fallback for FLEXT service."""
        mock_service = Mock()
        # Remove check_thresholds method to trigger fallback
        if hasattr(mock_service, "check_thresholds"):
            delattr(mock_service, "check_thresholds")

        manager = AlertManager(flext_alert_service=mock_service)

        violations = manager.check_thresholds({"error_rate": 10.0})
        assert violations == []

    def test_send_alert_basic(self) -> None:
        """Test basic alert sending."""
        manager = AlertManager()

        # This should not raise an exception
        manager.send_alert(
            AlertType.CONNECTIVITY_FAILURE,
            "Test message",
            AlertSeverity.HIGH,
            {"test": "context"},
        )

    def test_send_alert_with_flext_alerts(self) -> None:
        """Test alert sending with FLEXT alerts integration."""
        mock_alerts = Mock()
        manager = AlertManager(flext_alerts=mock_alerts)
        manager.flext_alerts = mock_alerts  # Ensure it's set

        manager.send_alert(
            AlertType.DATA_QUALITY_ISSUE,
            "Test data quality issue",
            AlertSeverity.MEDIUM,
            {"entity": "test"},
        )

        # Verify FLEXT alerts were called
        mock_alerts.trigger_alert.assert_called_once()
        call_args = mock_alerts.trigger_alert.call_args
        assert "GrupoNOS Pipeline: data_quality_issue" in call_args[1]["title"]
        assert call_args[1]["message"] == "Test data quality issue"
        assert call_args[1]["severity"] == AlertSeverity.MEDIUM

    def test_send_alert_without_flext_alerts(self) -> None:
        """Test alert sending without FLEXT alerts integration."""
        manager = AlertManager()

        # Should not raise an exception even without FLEXT alerts
        manager.send_alert(
            AlertType.THRESHOLD_BREACH,
            "Threshold exceeded",
            AlertSeverity.HIGH,
        )

    def test_connectivity_alert(self) -> None:
        """Test connectivity alert helper method."""
        manager = AlertManager()

        # Should not raise an exception
        manager.connectivity_alert("Oracle Database", "Connection timeout")

    def test_data_quality_alert_medium_severity(self) -> None:
        """Test data quality alert with medium severity."""
        manager = AlertManager()

        manager.data_quality_alert("allocation", "Missing required fields", "medium")

    def test_data_quality_alert_high_severity(self) -> None:
        """Test data quality alert with high severity."""
        manager = AlertManager()

        manager.data_quality_alert("order", "Critical data corruption", "high")

    def test_sync_timeout_alert(self) -> None:
        """Test sync timeout alert helper method."""
        manager = AlertManager()

        manager.sync_timeout_alert("allocation", 300)


class TestAlertTypeEnum:
    """Test AlertType enum values."""

    def test_alert_type_values(self) -> None:
        """Test that all AlertType enum values are correct."""
        assert AlertType.CONNECTIVITY_FAILURE.value == "connectivity_failure"
        assert AlertType.DATA_QUALITY_ISSUE.value == "data_quality_issue"
        assert AlertType.SYNC_TIMEOUT.value == "sync_timeout"
        assert AlertType.THRESHOLD_BREACH.value == "threshold_breach"
        assert AlertType.CONFIGURATION_ERROR.value == "configuration_error"
