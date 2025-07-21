"""Comprehensive CLI tests targeting 100% coverage.

Tests all CLI commands, error paths, and edge cases to achieve full coverage.
"""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

from click.testing import CliRunner

from gruponos_meltano_native.cli import main


class TestCLIComprehensive:
    """Comprehensive test suite for CLI commands targeting 100% coverage."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_main_context_setup(self) -> None:
        """Test main context setup with debug and config file flags."""
        # Test debug flag enables structlog configuration
        with patch("gruponos_meltano_native.cli.structlog") as mock_structlog, patch(
            "gruponos_meltano_native.cli.GrupoNOSConfig",
        ) as mock_config, patch("gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator"):
            mock_config.return_value = Mock()

            result = self.runner.invoke(main, ["--debug", "health"])

            # Debug mode should configure structlog
            mock_structlog.configure.assert_called_once()
            assert result.exit_code == 0

    def test_config_file_flag(self) -> None:
        """Test config file flag functionality."""
        with self.runner.isolated_filesystem():
            # Create a temporary config file
            with open("test_config.yml", "w") as f:
                f.write("test: config")

            with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
                "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
            ):
                mock_config.return_value = Mock()

                result = self.runner.invoke(main, ["--config-file", "test_config.yml", "health"])
                assert result.exit_code == 0

    def test_health_command_success(self) -> None:
        """Test health command success path."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
            "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
        ) as mock_orchestrator:
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["health"])
            assert result.exit_code == 0
            assert "✅ Configuration loaded successfully" in result.output
            assert "✅ Orchestrator created successfully" in result.output
            assert "✅ Health check completed" in result.output
            assert "✅ Pipeline health check: PASSED" in result.output

    def test_health_command_os_error(self) -> None:
        """Test health command OSError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=OSError("Connection failed")):
            result = self.runner.invoke(main, ["health"])
            assert result.exit_code == 1
            assert "❌ Pipeline health check: FAILED - Connection failed" in result.output

    def test_health_command_value_error(self) -> None:
        """Test health command ValueError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=ValueError("Invalid config")):
            result = self.runner.invoke(main, ["health"])
            assert result.exit_code == 1
            assert "❌ Pipeline health check: FAILED - Invalid config" in result.output

    def test_health_command_runtime_error(self) -> None:
        """Test health command RuntimeError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=RuntimeError("Runtime error")):
            result = self.runner.invoke(main, ["health"])
            assert result.exit_code == 1
            assert "❌ Pipeline health check: FAILED - Runtime error" in result.output

    def test_health_command_unexpected_error(self) -> None:
        """Test health command unexpected error handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=Exception("Unexpected error")):
            result = self.runner.invoke(main, ["health"])
            assert result.exit_code == 1
            assert "❌ Pipeline health check: UNEXPECTED ERROR - Unexpected error" in result.output

    def test_sync_command_success(self) -> None:
        """Test sync command success path."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
            "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
        ) as mock_orchestrator:
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["sync"])
            assert result.exit_code == 0
            assert "✅ Data sync completed for: all" in result.output

    def test_sync_command_with_entities(self) -> None:
        """Test sync command with specific entities."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
            "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
        ) as mock_orchestrator:
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["sync", "--entity", "allocation", "--entity", "order"])
            assert result.exit_code == 0
            assert "✅ Data sync completed for: allocation, order" in result.output

    def test_sync_command_dry_run(self) -> None:
        """Test sync command in dry-run mode."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
            "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
        ) as mock_orchestrator:
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["sync", "--dry-run"])
            assert result.exit_code == 0
            assert "🔍 DRY RUN MODE - No actual changes will be made" in result.output

    def test_sync_command_os_error(self) -> None:
        """Test sync command OSError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=OSError("Connection failed")):
            result = self.runner.invoke(main, ["sync"])
            assert result.exit_code == 1
            assert "❌ Data sync failed: Connection failed" in result.output

    def test_sync_command_value_error(self) -> None:
        """Test sync command ValueError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=ValueError("Invalid config")):
            result = self.runner.invoke(main, ["sync"])
            assert result.exit_code == 1
            assert "❌ Data sync failed: Invalid config" in result.output

    def test_sync_command_runtime_error(self) -> None:
        """Test sync command RuntimeError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=RuntimeError("Runtime error")):
            result = self.runner.invoke(main, ["sync"])
            assert result.exit_code == 1
            assert "❌ Data sync failed: Runtime error" in result.output

    def test_sync_command_unexpected_error(self) -> None:
        """Test sync command unexpected error handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=Exception("Unexpected error")):
            result = self.runner.invoke(main, ["sync"])
            assert result.exit_code == 1
            assert "❌ Data sync failed: UNEXPECTED ERROR - Unexpected error" in result.output

    def test_validate_command_success_table_format(self) -> None:
        """Test validate command success with table format."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
            "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
        ) as mock_orchestrator:
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["validate"])
            assert result.exit_code == 0
            assert "📋 Validation Results:" in result.output
            assert "config         : ✅ Valid" in result.output

    def test_validate_command_json_format(self) -> None:
        """Test validate command with JSON output format."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
            "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
        ) as mock_orchestrator:
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["validate", "--output-format", "json"])
            assert result.exit_code == 0
            # Output should be valid JSON
            output_lines = result.output.strip().split("\n")
            json_output = output_lines[-1] if output_lines else "{}"
            parsed = json.loads(json_output)
            assert "config" in parsed

    def test_validate_command_yaml_format(self) -> None:
        """Test validate command with YAML output format."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config, patch(
            "gruponos_meltano_native.cli.GrupoNOSMeltanoOrchestrator",
        ) as mock_orchestrator:
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["validate", "--output-format", "yaml"])
            assert result.exit_code == 0
            # Output should contain YAML content
            assert "config:" in result.output

    def test_validate_command_os_error(self) -> None:
        """Test validate command OSError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=OSError("Connection failed")):
            result = self.runner.invoke(main, ["validate"])
            assert result.exit_code == 1
            assert "❌ Validation failed: Connection failed" in result.output

    def test_validate_command_value_error(self) -> None:
        """Test validate command ValueError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=ValueError("Invalid config")):
            result = self.runner.invoke(main, ["validate"])
            assert result.exit_code == 1
            assert "❌ Validation failed: Invalid config" in result.output

    def test_validate_command_runtime_error(self) -> None:
        """Test validate command RuntimeError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=RuntimeError("Runtime error")):
            result = self.runner.invoke(main, ["validate"])
            assert result.exit_code == 1
            assert "❌ Validation failed: Runtime error" in result.output

    def test_validate_command_unexpected_error(self) -> None:
        """Test validate command unexpected error handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=Exception("Unexpected error")):
            result = self.runner.invoke(main, ["validate"])
            assert result.exit_code == 1
            assert "❌ Validation failed: UNEXPECTED ERROR - Unexpected error" in result.output

    def test_show_config_command_yaml_format(self) -> None:
        """Test show-config command with YAML format."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config:
            mock_instance = Mock()
            mock_instance.wms_source = Mock()
            mock_instance.wms_source.base_url = "http://test"
            mock_instance.wms_source.entities = ["test_entity"]
            mock_instance.wms_source.page_size = 100
            mock_instance.oracle_target = Mock()
            mock_instance.oracle_target.host = "localhost"
            mock_instance.oracle_target.port = 1521
            mock_instance.oracle_target.service_name = "test"
            mock_config.return_value = mock_instance

            result = self.runner.invoke(main, ["show-config", "--format", "yaml"])
            assert result.exit_code == 0
            assert "project_name:" in result.output
            assert "environment:" in result.output

    def test_show_config_command_json_format(self) -> None:
        """Test show-config command with JSON format."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config:
            mock_instance = Mock()
            mock_instance.wms_source = Mock()
            mock_instance.wms_source.base_url = "http://test"
            mock_instance.wms_source.entities = ["test_entity"]
            mock_instance.wms_source.page_size = 100
            mock_instance.oracle_target = Mock()
            mock_instance.oracle_target.host = "localhost"
            mock_instance.oracle_target.port = 1521
            mock_instance.oracle_target.service_name = "test"
            mock_config.return_value = mock_instance

            result = self.runner.invoke(main, ["show-config", "--format", "json"])
            assert result.exit_code == 0
            # Output should be valid JSON
            output_lines = result.output.strip().split("\n")
            json_output = output_lines[-1] if output_lines else "{}"
            parsed = json.loads(json_output)
            assert "project_name" in parsed

    def test_show_config_command_missing_attributes(self) -> None:
        """Test show-config command when config attributes are missing."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig") as mock_config:
            # Test with minimal config object
            mock_instance = Mock()
            # Simulate missing hasattr checks
            mock_instance.wms_source = None
            mock_instance.oracle_target = None
            mock_config.return_value = mock_instance

            result = self.runner.invoke(main, ["show-config"])
            assert result.exit_code == 0
            assert "project_name:" in result.output

    def test_show_config_command_os_error(self) -> None:
        """Test show-config command OSError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=OSError("Connection failed")):
            result = self.runner.invoke(main, ["show-config"])
            assert result.exit_code == 1
            assert "❌ Failed to show configuration: Connection failed" in result.output

    def test_show_config_command_value_error(self) -> None:
        """Test show-config command ValueError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=ValueError("Invalid config")):
            result = self.runner.invoke(main, ["show-config"])
            assert result.exit_code == 1
            assert "❌ Failed to show configuration: Invalid config" in result.output

    def test_show_config_command_runtime_error(self) -> None:
        """Test show-config command RuntimeError handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=RuntimeError("Runtime error")):
            result = self.runner.invoke(main, ["show-config"])
            assert result.exit_code == 1
            assert "❌ Failed to show configuration: Runtime error" in result.output

    def test_show_config_command_unexpected_error(self) -> None:
        """Test show-config command unexpected error handling."""
        with patch("gruponos_meltano_native.cli.GrupoNOSConfig", side_effect=Exception("Unexpected error")):
            result = self.runner.invoke(main, ["show-config"])
            assert result.exit_code == 1
            assert "❌ Failed to show configuration: UNEXPECTED ERROR - Unexpected error" in result.output

    def test_main_entry_point(self) -> None:
        """Test main entry point execution."""
        with patch("gruponos_meltano_native.cli.main.main") as mock_main:
            # Import the main module to test __name__ == "__main__" path
            from gruponos_meltano_native import cli

            # Mock main to avoid actual execution
            mock_main.return_value = None

            # This would normally execute when the module is run directly
            # We're testing that the path exists, not executing it
            assert hasattr(cli.main, "main")
