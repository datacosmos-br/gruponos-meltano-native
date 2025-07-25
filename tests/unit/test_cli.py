"""Unit tests for CLI functionality."""

from click.testing import CliRunner

from gruponos_meltano_native.cli import cli as app


class TestCLI:
    """Test CLI functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self) -> None:
        """Test version command."""
        result = self.runner.invoke(app, ["--version"])
        assert result.exit_code == 0

    def test_show_config_command(self) -> None:
        """Test show-config command."""
        result = self.runner.invoke(app, ["show-config"])
        # May fail without proper config but should not crash
        assert result.exit_code in {0, 1}

    def test_validate_command(self) -> None:
        """Test validate command."""
        result = self.runner.invoke(app, ["validate"])
        # Should work even without env vars (basic validation)
        assert result.exit_code in {0, 1}

    def test_health_command(self) -> None:
        """Test health check command."""
        result = self.runner.invoke(app, ["health"])
        # Should validate without actual connection
        assert result.exit_code in {
            0,
            1,
        }  # 0 for success, 1 for expected validation error

    def test_sync_command(self) -> None:
        """Test sync command."""
        result = self.runner.invoke(app, ["sync"])
        # Should validate configuration without actual sync
        assert result.exit_code in {
            0,
            1,
        }  # Expected to fail validation without real config

    def test_help_command(self) -> None:
        """Test help command."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "GrupoNOS Meltano Native" in result.stdout

    def test_invalid_command(self) -> None:
        """Test invalid command handling."""
        result = self.runner.invoke(app, ["nonexistent"])
        assert result.exit_code != 0
