"""Tests for CLI main module."""

from click.testing import CliRunner

from Claude45_Demo.cli.main import cli


class TestCLI:
    """Test CLI commands."""

    def test_cli_help(self) -> None:
        """Test CLI shows help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Aker Investment Platform" in result.output
        assert "Real Estate Analysis Tool" in result.output

    def test_cli_version(self) -> None:
        """Test CLI shows version."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_verbose_flag(self) -> None:
        """Test verbose flag is recognized."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "--help"])

        assert result.exit_code == 0


class TestScreenCommand:
    """Test screen command."""

    def test_screen_help(self) -> None:
        """Test screen command shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["screen", "--help"])

        assert result.exit_code == 0
        assert "Screen multiple submarkets" in result.output

    def test_screen_requires_input(self) -> None:
        """Test screen command requires input file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["screen"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_screen_not_implemented_message(self) -> None:
        """Test screen command shows not implemented message."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a dummy input file
            with open("test.csv", "w") as f:
                f.write("name,lat,lon,state\nBoulder,40.0,-105.3,CO\n")

            result = runner.invoke(cli, ["screen", "--input", "test.csv"])

            assert result.exit_code == 0
            assert "not yet implemented" in result.output


class TestAnalyzeCommand:
    """Test analyze command."""

    def test_analyze_help(self) -> None:
        """Test analyze command shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])

        assert result.exit_code == 0
        assert "Perform detailed analysis" in result.output

    def test_analyze_requires_address(self) -> None:
        """Test analyze command requires address."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code != 0

    def test_analyze_not_implemented_message(self) -> None:
        """Test analyze command shows not implemented message."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["analyze", "--address", "123 Main St, Boulder, CO"]
        )

        assert result.exit_code == 0
        assert "not yet implemented" in result.output


class TestReportCommand:
    """Test report command."""

    def test_report_help(self) -> None:
        """Test report command shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "--help"])

        assert result.exit_code == 0
        assert "Generate formatted reports" in result.output

    def test_report_requires_market(self) -> None:
        """Test report command requires market."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report"])

        assert result.exit_code != 0

    def test_report_not_implemented_message(self) -> None:
        """Test report command shows not implemented message."""
        runner = CliRunner()
        result = runner.invoke(cli, ["report", "--market", "Boulder, CO"])

        assert result.exit_code == 0
        assert "not yet implemented" in result.output


class TestDataCommands:
    """Test data management commands."""

    def test_data_help(self) -> None:
        """Test data command shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["data", "--help"])

        assert result.exit_code == 0
        assert "Data management commands" in result.output

    def test_data_status(self) -> None:
        """Test data status command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["data", "status"])

        assert result.exit_code == 0
        assert "Cache Status" in result.output

    def test_data_refresh(self) -> None:
        """Test data refresh command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["data", "refresh", "--all"])

        assert result.exit_code == 0
        assert "Data Refresh" in result.output

    def test_data_clear_requires_confirmation(self) -> None:
        """Test data clear command requires confirmation."""
        runner = CliRunner()
        # Without confirmation, should abort
        result = runner.invoke(cli, ["data", "clear", "--all"], input="n\n")

        assert result.exit_code == 1  # Aborted


class TestConfigCommands:
    """Test configuration commands."""

    def test_config_help(self) -> None:
        """Test config command shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "--help"])

        assert result.exit_code == 0
        assert "Configuration management" in result.output

    def test_config_init(self) -> None:
        """Test config init command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "init"])

        assert result.exit_code == 0
        assert "Configuration Setup" in result.output

    def test_config_show(self) -> None:
        """Test config show command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "show"])

        assert result.exit_code == 0
        assert "Current Configuration" in result.output

    def test_config_set(self) -> None:
        """Test config set command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set", "test_key", "test_value"])

        assert result.exit_code == 0
        assert "test_key" in result.output

    def test_config_get(self) -> None:
        """Test config get command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "get", "test_key"])

        assert result.exit_code == 0
