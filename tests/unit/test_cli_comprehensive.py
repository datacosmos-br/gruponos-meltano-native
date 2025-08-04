"""Comprehensive CLI tests targeting 100% coverage.

Tests all CLI commands, error paths, and edge cases to achieve full coverage.
"""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

from click.testing import CliRunner

from gruponos_meltano_native import cli
from gruponos_meltano_native.cli import cli as main


class TestCLIComprehensive:
    """Comprehensive test suite for CLI commands targeting 100% coverage."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_main_context_setup(self) -> None:
        """Test main context setup with debug and config file flags."""
        # Test debug flag enables FLEXT logging configuration
        with (
            patch("gruponos_meltano_native.cli.setup_logging") as mock_setup_logging,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch("gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator"),
        ):
            mock_config.return_value = Mock()

            result = self.runner.invoke(main, ["--debug", "health"])

            # Debug mode should configure FLEXT logging
            mock_setup_logging.assert_called_once()
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)

    def test_config_file_flag(self) -> None:
        """Test config file flag functionality."""
        with self.runner.isolated_filesystem():
            # Create a temporary config file
            with open("test_config.yml", "w", encoding="utf-8") as f:
                f.write("test: config")

            with (
                patch(
                    "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
                ) as mock_config,
                patch(
                    "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
                ),
            ):
                mock_config.return_value = Mock()

                result = self.runner.invoke(
                    main,
                    ["--config-file", "test_config.yml", "health"],
                )
                if result.exit_code != 0:
                    msg = f"Expected {0}, got {result.exit_code}"
                    raise AssertionError(msg)

    def test_health_command_success(self) -> None:
        """Test health command success path."""
        with (
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
            ) as mock_orchestrator,
        ):
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["health"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            if "✅ Pipeline health check: PASSED" not in result.output:
                msg = (
                    f"Expected {'✅ Pipeline health check: PASSED'} in {result.output}"
                )
                raise AssertionError(msg)

    def test_health_command_os_error(self) -> None:
        """Test health command OSError handling (unhandled exception)."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=OSError("Connection failed"),
        ):
            result = self.runner.invoke(main, ["health"])
            # OSError is not explicitly caught by health command, so it bubbles up
            # Click runner catches it and returns exit code 1, but no custom message
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            # Since OSError is not caught, the error message won't be formatted
            # but the command will still fail

    def test_health_command_value_error(self) -> None:
        """Test health command ValueError handling."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=ValueError("Invalid config"),
        ):
            result = self.runner.invoke(main, ["health"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            if "❌ Pipeline health check: FAILED - Invalid config" not in result.output:
                msg = f"Expected {'❌ Pipeline health check: FAILED - Invalid config'} in {result.output}"
                raise AssertionError(msg)

    def test_health_command_runtime_error(self) -> None:
        """Test health command RuntimeError handling."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=RuntimeError("Runtime error"),
        ):
            result = self.runner.invoke(main, ["health"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            if "❌ Pipeline health check: FAILED - Runtime error" not in result.output:
                msg = f"Expected {'❌ Pipeline health check: FAILED - Runtime error'} in {result.output}"
                raise AssertionError(msg)

    def test_health_command_unexpected_error(self) -> None:
        """Test health command unexpected error handling."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=Exception("Unexpected error"),
        ):
            result = self.runner.invoke(main, ["health"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            assert (
                "❌ Pipeline health check: UNEXPECTED ERROR - Unexpected error"
                in result.output
            )

    def test_health_command_success_with_oracle_config(self) -> None:
        """Test health command success path with Oracle configuration."""
        with (
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
            ) as mock_orchestrator,
        ):
            # Mock configuration with Oracle settings
            mock_config.return_value = Mock()
            mock_config.return_value.oracle = Mock()
            mock_config.return_value.oracle.host = "localhost"
            mock_config.return_value.oracle.username = "user"
            mock_config.return_value.oracle.password = "pass"
            mock_config.return_value.meltano_project_root = "/path"
            mock_config.return_value.meltano_environment = "dev"
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["health"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            if "✅ Pipeline health check: PASSED" not in result.output:
                msg = (
                    f"Expected {'✅ Pipeline health check: PASSED'} in {result.output}"
                )
                raise AssertionError(msg)

    def test_list_pipelines_command(self) -> None:
        """Test list-pipelines command."""
        with (
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
            ) as mock_orchestrator,
        ):
            mock_config.return_value = Mock()
            mock_orchestrator_instance = Mock()
            mock_orchestrator.return_value = mock_orchestrator_instance

            # Mock pipeline listing - use correct method name
            mock_orchestrator_instance.list_pipelines.return_value = [
                "test-pipeline",
                "another-pipeline",
            ]

            result = self.runner.invoke(main, ["list-pipelines"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            if "Available pipelines:" not in result.output:
                msg = f"Expected 'Available pipelines:' in {result.output}"
                raise AssertionError(msg)

    def test_run_command_dry_run(self) -> None:
        """Test run command in dry-run mode."""
        with (
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
            ) as mock_orchestrator,
        ):
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["run", "test-pipeline", "--dry-run"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            if "🔍 DRY RUN MODE - No actual changes will be made" not in result.output:
                msg = f"Expected {'🔍 DRY RUN MODE - No actual changes will be made'} in {result.output}"
                raise AssertionError(msg)

    def test_health_command_configuration_runtime_error(self) -> None:
        """Test health command RuntimeError during configuration loading."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=RuntimeError("Configuration failed"),
        ):
            result = self.runner.invoke(main, ["health"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            if "❌ Pipeline health check: FAILED" not in result.output:
                msg = f"Expected '❌ Pipeline health check: FAILED' in {result.output}"
                raise AssertionError(msg)

    def test_validate_command_value_error(self) -> None:
        """Test validate command ValueError handling."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=ValueError("Invalid config"),
        ):
            result = self.runner.invoke(main, ["validate"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            if "❌ Validation failed" not in result.output:
                msg = f"Expected '❌ Validation failed' in {result.output}"
                raise AssertionError(msg)

    def test_validate_command_runtime_error(self) -> None:
        """Test validate command RuntimeError handling."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=RuntimeError("Runtime error"),
        ):
            result = self.runner.invoke(main, ["validate"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            if "❌ Validation failed: Runtime error" not in result.output:
                msg = f"Expected {'❌ Validation failed: Runtime error'} in {result.output}"
                raise AssertionError(msg)

    def test_validate_command_unexpected_error(self) -> None:
        """Test validate command unexpected error handling (unhandled exception)."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=Exception("Unexpected error"),
        ):
            result = self.runner.invoke(main, ["validate"])
            # Generic Exception is not explicitly caught by validate command, so it bubbles up
            # Click runner catches it and returns exit code 1, but no custom message
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            # Since generic Exception is not caught, the error message won't be formatted
            # but the command will still fail

    def test_validate_command_success_table_format(self) -> None:
        """Test validate command success with table format."""
        with (
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
            ) as mock_orchestrator,
        ):
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["validate"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            if "📋 Validation Results:" not in result.output:
                msg = f"Expected {'📋 Validation Results:'} in {result.output}"
                raise AssertionError(msg)
            assert "config         : ✅ Valid" in result.output

    def test_validate_command_json_format(self) -> None:
        """Test validate command with JSON output format."""
        with (
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
            ) as mock_orchestrator,
        ):
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["validate", "--output-format", "json"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            # Extract JSON from output (skip log messages)
            output_lines = result.output.strip().split("\n")
            # Find the first line that starts with '{'
            json_lines = []
            found_json = False
            for line in output_lines:
                if line.strip().startswith("{"):
                    found_json = True
                if found_json:
                    json_lines.append(line)
            json_output = "\n".join(json_lines)
            parsed = json.loads(json_output)
            if "config" not in parsed:
                msg = f"Expected {'config'} in {parsed}"
                raise AssertionError(msg)

    def test_validate_command_yaml_format(self) -> None:
        """Test validate command with YAML output format."""
        with (
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            ) as mock_config,
            patch(
                "gruponos_meltano_native.cli.create_gruponos_meltano_orchestrator",
            ) as mock_orchestrator,
        ):
            mock_config.return_value = Mock()
            mock_orchestrator.return_value = Mock()

            result = self.runner.invoke(main, ["validate", "--output-format", "yaml"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            # Output should contain YAML content
            if "config:" not in result.output:
                msg = f"Expected {'config:'} in {result.output}"
                raise AssertionError(msg)

    def test_validate_command_os_error(self) -> None:
        """Test validate command OSError handling (unhandled exception)."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=OSError("Connection failed"),
        ):
            result = self.runner.invoke(main, ["validate"])
            # OSError is not explicitly caught by validate command, so it bubbles up
            # Click runner catches it and returns exit code 1, but no custom message
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            # Since OSError is not caught, the error message won't be formatted
            # but the command will still fail

    def test_show_config_command_yaml_format(self) -> None:
        """Test show-config command with YAML format."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
        ) as mock_config:
            mock_instance = Mock()
            # Set the environment attribute to a string value
            mock_instance.environment = "development"
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
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            if "project_name:" not in result.output:
                msg = f"Expected {'project_name:'} in {result.output}"
                raise AssertionError(msg)
            assert "environment:" in result.output

    def test_show_config_command_json_format(self) -> None:
        """Test show-config command with JSON format."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
        ) as mock_config:
            mock_instance = Mock()
            # Set the environment attribute to a string value
            mock_instance.environment = "development"
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
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            # Extract JSON from output (skip log messages)
            output_lines = result.output.strip().split("\n")
            # Find the first line that starts with '{'
            json_lines = []
            found_json = False
            for line in output_lines:
                if line.strip().startswith("{"):
                    found_json = True
                if found_json:
                    json_lines.append(line)
            json_output = "\n".join(json_lines)
            parsed = json.loads(json_output)
            if "project_name" not in parsed:
                msg = f"Expected {'project_name'} in {parsed}"
                raise AssertionError(msg)
            if parsed["environment"] != "development":
                msg = f"Expected {'development'}, got {parsed['environment']}"
                raise AssertionError(msg)

    def test_show_config_command_missing_attributes(self) -> None:
        """Test show-config command when config attributes are missing."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
        ) as mock_config:
            # Test with minimal config object - provide all required attributes
            mock_instance = Mock()
            # Configure all required attributes for CLI
            mock_instance.app_name = "gruponos-meltano-native"
            mock_instance.version = "0.9.0"
            mock_instance.environment = "test"
            mock_instance.debug = False
            mock_instance.log_level = "INFO"
            mock_instance.oracle = None
            mock_instance.wms_source = None
            mock_instance.target_oracle = None
            mock_instance.job = Mock()
            mock_instance.job.job_name = "test-job"
            mock_instance.job.schedule = "0 0 * * *"
            mock_instance.job.timeout_minutes = 60
            mock_instance.job.retry_attempts = 3
            mock_instance.job.retry_delay_seconds = 30
            mock_instance.meltano_project_root = "/test/project"
            mock_instance.meltano_environment = "dev"
            mock_instance.meltano_state_backend = "filesystem"
            mock_config.return_value = mock_instance

            result = self.runner.invoke(main, ["show-config"])
            if result.exit_code != 0:
                msg = f"Expected {0}, got {result.exit_code}"
                raise AssertionError(msg)
            if "app_name:" not in result.output:
                msg = f"Expected {'app_name:'} in {result.output}"
                raise AssertionError(msg)

    def test_show_config_command_os_error(self) -> None:
        """Test show-config command OSError handling (unhandled exception)."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=OSError("Connection failed"),
        ):
            result = self.runner.invoke(main, ["show-config"])
            # OSError is not explicitly caught by show-config command, so it bubbles up
            # Click runner catches it and returns exit code 1, but no custom message
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            # Since OSError is not caught, the error message won't be formatted
            # but the command will still fail

    def test_show_config_command_value_error(self) -> None:
        """Test show-config command ValueError handling."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=ValueError("Invalid config"),
        ):
            result = self.runner.invoke(main, ["show-config"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            if "❌ Failed to show configuration: Invalid config" not in result.output:
                msg = f"Expected {'❌ Failed to show configuration: Invalid config'} in {result.output}"
                raise AssertionError(msg)

    def test_show_config_command_runtime_error(self) -> None:
        """Test show-config command RuntimeError handling."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=RuntimeError("Runtime error"),
        ):
            result = self.runner.invoke(main, ["show-config"])
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            if "❌ Failed to show configuration: Runtime error" not in result.output:
                msg = f"Expected {'❌ Failed to show configuration: Runtime error'} in {result.output}"
                raise AssertionError(msg)

    def test_show_config_command_unexpected_error(self) -> None:
        """Test show-config command unexpected error handling (unhandled exception)."""
        with patch(
            "gruponos_meltano_native.cli.create_gruponos_meltano_settings",
            side_effect=Exception("Unexpected error"),
        ):
            result = self.runner.invoke(main, ["show-config"])
            # Generic Exception is not explicitly caught by show-config command, so it bubbles up
            # Click runner catches it and returns exit code 1, but no custom message
            if result.exit_code != 1:
                msg = f"Expected {1}, got {result.exit_code}"
                raise AssertionError(msg)
            # Since generic Exception is not caught, the error message won't be formatted
            # but the command will still fail

    def test_main_entry_point(self) -> None:
        """Test main entry point execution."""
        with patch("gruponos_meltano_native.cli.main.main") as mock_main:
            # Import the main module to test __name__ == "__main__" path

            # Mock main to avoid actual execution
            mock_main.return_value = None

            # This would normally execute when the module is run directly
            # We're testing that the path exists, not executing it
            assert hasattr(cli.main, "main")
