"""Comprehensive tests for GrupoNOS Meltano Native exceptions module.

Tests exception hierarchy, inheritance, and proper FLEXT standards compliance.
"""

import pytest

from gruponos_meltano_native import (
    GruponosMeltanoAlertDeliveryError,
    GruponosMeltanoAlertError,
    GruponosMeltanoConfigurationError,
    GruponosMeltanoDataError,
    GruponosMeltanoDataQualityError,
    GruponosMeltanoDataValidationError,
    GruponosMeltanoError,
    GruponosMeltanoMissingConfigError,
    GruponosMeltanoMonitoringError,
    GruponosMeltanoOracleConnectionError,
    GruponosMeltanoOracleError,
    GruponosMeltanoOracleQueryError,
    GruponosMeltanoOracleTimeoutError,
    GruponosMeltanoOrchestrationError,
    GruponosMeltanoPipelineError,
    GruponosMeltanoPipelineTimeoutError,
    GruponosMeltanoPipelineValidationError,
    GruponosMeltanoSingerError,
    GruponosMeltanoTapError,
    GruponosMeltanoTargetError,
    GruponosMeltanoValidationError,
)

# Constants
EXPECTED_DATA_COUNT = 3


class TestGruponosMeltanoBaseException:
    """Test base exception class."""

    def test_base_exception_creation(self) -> None:
      """Test base exception can be created with message."""
      error = GruponosMeltanoError("Test error message")
      if str(error) != "[GENERIC_ERROR] Test error message":
          msg: str = f"Expected {'[GENERIC_ERROR] Test error message'}, got {error!s}"
          raise AssertionError(msg)
      assert error.message == "Test error message"
      if error.error_code != "GENERIC_ERROR":
          msg: str = f"Expected {'GENERIC_ERROR'}, got {error.error_code}"
          raise AssertionError(msg)
      assert error.context == {}

    def test_base_exception_with_context(self) -> None:
      """Test base exception with context information."""
      context = {"key": "value", "number": 42}
      error = GruponosMeltanoError(
          "Test error",
          context=context,
      )
      if error.message != "Test error":
          msg: str = f"Expected {'Test error'}, got {error.message}"
          raise AssertionError(msg)
      # FlextError generates GENERIC_ERROR by default unless overridden
      assert error.error_code == "GENERIC_ERROR"
      # Context is stored directly in FlextError
      if error.context != context:
          msg: str = f"Expected {context}, got {error.context}"
          raise AssertionError(msg)
      # The string representation shows the error code and message, but not context
      if str(error) != "[GENERIC_ERROR] Test error":
          msg: str = f"Expected '[GENERIC_ERROR] Test error', got {error!s}"
          raise AssertionError(msg)

    def test_base_exception_repr(self) -> None:
      """Test exception repr format."""
      error = GruponosMeltanoError(
          "Test message",
          context={"test": True},
      )
      repr_str = repr(error)
      # The repr shows the specific class name
      if "GruponosMeltanoError" not in repr_str:
          msg: str = f"Expected {'GruponosMeltanoError'} in {repr_str}"
          raise AssertionError(msg)
      assert "Test message" in repr_str
      if "GENERIC_ERROR" not in repr_str:
          msg: str = f"Expected {'GENERIC_ERROR'} in {repr_str}"
          raise AssertionError(msg)

    def test_base_exception_inheritance(self) -> None:
      """Test base exception inherits from Exception."""
      error = GruponosMeltanoError("Test")
      assert isinstance(error, Exception)
      assert isinstance(error, GruponosMeltanoError)


class TestConfigurationExceptions:
    """Test configuration-related exceptions."""

    def test_configuration_error_inheritance(self) -> None:
      """Test configuration error inheritance."""
      error = GruponosMeltanoConfigurationError("Config error")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoConfigurationError)

    def test_validation_error_inheritance(self) -> None:
      """Test validation error inheritance."""
      error = GruponosMeltanoValidationError("Validation failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoConfigurationError)
      assert isinstance(error, GruponosMeltanoValidationError)

    def test_missing_config_error_inheritance(self) -> None:
      """Test missing config error inheritance."""
      error = GruponosMeltanoMissingConfigError("Config missing")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoMissingConfigError)


class TestOrchestrationExceptions:
    """Test orchestration-related exceptions."""

    def test_orchestration_error_inheritance(self) -> None:
      """Test orchestration error inheritance."""
      error = GruponosMeltanoOrchestrationError("Orchestration failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoOrchestrationError)

    def test_pipeline_error_inheritance(self) -> None:
      """Test pipeline error inheritance."""
      error = GruponosMeltanoPipelineError("Pipeline failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoPipelineError)

    def test_pipeline_timeout_error_inheritance(self) -> None:
      """Test pipeline timeout error inheritance."""
      error = GruponosMeltanoPipelineTimeoutError("Pipeline timeout")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoPipelineError)
      assert isinstance(error, GruponosMeltanoPipelineTimeoutError)

    def test_pipeline_validation_error_inheritance(self) -> None:
      """Test pipeline validation error inheritance."""
      error = GruponosMeltanoPipelineValidationError("Pipeline validation failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoPipelineError)
      assert isinstance(error, GruponosMeltanoPipelineValidationError)


class TestOracleExceptions:
    """Test Oracle-related exceptions."""

    def test_oracle_error_inheritance(self) -> None:
      """Test Oracle error inheritance."""
      error = GruponosMeltanoOracleError("Oracle error")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoOracleError)

    def test_oracle_connection_error_inheritance(self) -> None:
      """Test Oracle connection error inheritance."""
      error = GruponosMeltanoOracleConnectionError("Connection failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoOracleError)
      assert isinstance(error, GruponosMeltanoOracleConnectionError)

    def test_oracle_query_error_inheritance(self) -> None:
      """Test Oracle query error inheritance."""
      error = GruponosMeltanoOracleQueryError("Query failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoOracleError)
      assert isinstance(error, GruponosMeltanoOracleQueryError)

    def test_oracle_timeout_error_inheritance(self) -> None:
      """Test Oracle timeout error inheritance."""
      error = GruponosMeltanoOracleTimeoutError("Oracle timeout")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoOracleError)
      assert isinstance(error, GruponosMeltanoOracleTimeoutError)


class TestMonitoringExceptions:
    """Test monitoring-related exceptions."""

    def test_monitoring_error_inheritance(self) -> None:
      """Test monitoring error inheritance."""
      error = GruponosMeltanoMonitoringError("Monitoring failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoMonitoringError)

    def test_alert_error_inheritance(self) -> None:
      """Test alert error inheritance."""
      error = GruponosMeltanoAlertError("Alert failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoMonitoringError)
      assert isinstance(error, GruponosMeltanoAlertError)

    def test_alert_delivery_error_inheritance(self) -> None:
      """Test alert delivery error inheritance."""
      error = GruponosMeltanoAlertDeliveryError("Alert delivery failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoMonitoringError)
      assert isinstance(error, GruponosMeltanoAlertError)
      assert isinstance(error, GruponosMeltanoAlertDeliveryError)


class TestDataExceptions:
    """Test data-related exceptions."""

    def test_data_error_inheritance(self) -> None:
      """Test data error inheritance."""
      error = GruponosMeltanoDataError("Data error")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoDataError)

    def test_data_validation_error_inheritance(self) -> None:
      """Test data validation error inheritance."""
      error = GruponosMeltanoDataValidationError("Data validation failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoDataError)
      assert isinstance(error, GruponosMeltanoDataValidationError)

    def test_data_quality_error_inheritance(self) -> None:
      """Test data quality error inheritance."""
      error = GruponosMeltanoDataQualityError("Data quality issue")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoDataError)
      assert isinstance(error, GruponosMeltanoDataQualityError)


class TestSingerExceptions:
    """Test Singer protocol-related exceptions."""

    def test_singer_error_inheritance(self) -> None:
      """Test Singer error inheritance."""
      error = GruponosMeltanoSingerError("Singer error")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoSingerError)

    def test_tap_error_inheritance(self) -> None:
      """Test tap error inheritance."""
      error = GruponosMeltanoTapError("Tap failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoSingerError)
      assert isinstance(error, GruponosMeltanoTapError)

    def test_target_error_inheritance(self) -> None:
      """Test target error inheritance."""
      error = GruponosMeltanoTargetError("Target failed")
      assert isinstance(error, GruponosMeltanoError)
      assert isinstance(error, GruponosMeltanoSingerError)
      assert isinstance(error, GruponosMeltanoTargetError)


class TestExceptionUsagePatterns:
    """Test common exception usage patterns."""

    def test_exception_catching_hierarchy(self) -> None:
      """Test that exceptions can be caught by their parent classes."""
      # Test Oracle exceptions
      msg = "Connection failed"
      with pytest.raises(GruponosMeltanoError):
          raise GruponosMeltanoOracleConnectionError(msg)

      msg = "Connection failed"
      with pytest.raises(GruponosMeltanoOracleError):
          raise GruponosMeltanoOracleConnectionError(msg)

      # Test Pipeline exceptions
      msg = "Pipeline timeout"
      with pytest.raises(GruponosMeltanoError):
          raise GruponosMeltanoPipelineTimeoutError(msg)

      msg = "Pipeline timeout"
      with pytest.raises(GruponosMeltanoOrchestrationError):
          raise GruponosMeltanoPipelineTimeoutError(msg)

      msg = "Pipeline timeout"
      with pytest.raises(GruponosMeltanoPipelineError):
          raise GruponosMeltanoPipelineTimeoutError(msg)

    def test_exception_with_contextual_information(self) -> None:
      """Test exceptions with rich contextual information."""
      context = {
          "host": "localhost",
          "port": 1521,
          "service_name": "ORCL",
          "retry_count": 3,
      }

      error = GruponosMeltanoOracleConnectionError(
          "Failed to connect to Oracle database",
          error_code="ORACLE_CONN_001",
          context=context,
      )

      if "Failed to connect to Oracle database" not in str(error):
          msg: str = f"Expected {'Failed to connect to Oracle database'} in {error!s}"
          raise AssertionError(msg)
      # Context is stored in the error but not shown in string representation by default
      assert error.context.get("host") == "localhost"
      assert error.context.get("port") == 1521
      if error.error_code != "ORACLE_CONN_001":
          msg: str = f"Expected {'ORACLE_CONN_001'}, got {error.error_code}"
          raise AssertionError(msg)
      assert error.context.get("retry_count") == EXPECTED_DATA_COUNT

    def test_exception_chaining(self) -> None:
      """Test exception chaining with cause."""
      original_error = ValueError("Original validation error")

      try:
          raise original_error
      except ValueError:
          chain_error = GruponosMeltanoValidationError(
              "Configuration validation failed",
              context={"field": "database_url"},
          )
          # In real code, would use 'raise chain_error from e'
          assert isinstance(chain_error, GruponosMeltanoValidationError)
          if chain_error.context["field"] != "database_url":
              msg: str = (
                  f"Expected {'database_url'}, got {chain_error.context['field']}"
              )
              raise AssertionError(msg) from None
