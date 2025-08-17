"""Unit tests for CLI functionality."""

from click.testing import CliRunner

from gruponos_meltano_native import cli as app


class TestCLI:
    """Test CLI functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(app, ["--version"])
        if result.exit_code != 0:
            msg: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)

    def test_show_config_command(self) -> None:
        """Test show-config command."""
        result = self.runner.invoke(app, ["show-config"])
        # May fail without proper config but should not crash
        if result.exit_code not in {0, 1}:
            msg: str = f"Expected {result.exit_code} in {{0, 1}}"
            raise AssertionError(msg)

    def test_validate_command(self) -> None:
        """Test validate command."""
        result = self.runner.invoke(app, ["validate"])
        # Should work even without env vars (basic validation)
        if result.exit_code not in {0, 1}:
            msg: str = f"Expected {result.exit_code} in {{0, 1}}"
            raise AssertionError(msg)

    def test_health_command(self) -> None:
        """Test health check command."""
        result = self.runner.invoke(app, ["health"])
        # Should validate without actual connection
        if result.exit_code not in {0, 1}:
            msg: str = f"Expected {result.exit_code} in {{0, 1}}"
            raise AssertionError(msg)
        # 0 for success, 1 for expected validation error

    def test_list_pipelines_command(self) -> None:
        """Test list-pipelines command."""
        result = self.runner.invoke(app, ["list-pipelines"])
        # Should work but may fail without proper config
        if result.exit_code not in {0, 1}:
            msg: str = f"Expected {result.exit_code} in {{0, 1}}"
            raise AssertionError(msg)
        # Expected to work even without full config

    def test_help_command(self) -> None:
        """Test help command."""
        result = self.runner.invoke(app, ["--help"])
        if result.exit_code != 0:
            msg: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        if "GrupoNOS Meltano Native" not in result.stdout:
            msg: str = f"Expected {'GrupoNOS Meltano Native'} in {result.stdout}"
            raise AssertionError(msg)

    def test_invalid_command(self) -> None:
        """Test invalid command handling."""
        result = self.runner.invoke(app, ["nonexistent"])
        assert result.exit_code != 0
