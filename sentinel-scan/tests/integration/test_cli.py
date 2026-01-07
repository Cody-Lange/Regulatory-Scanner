"""Integration tests for CLI."""

from typer.testing import CliRunner

from sentinel_scan.cli import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_version(self):
        """Verify --version flag works."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "sentinel-scan version" in result.stdout

    def test_help(self):
        """Verify --help flag works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Sentinel Scan" in result.stdout

    def test_scan_help(self):
        """Verify scan --help works."""
        result = runner.invoke(app, ["scan", "--help"])
        assert result.exit_code == 0
        assert "Scan files for compliance violations" in result.stdout

    def test_init_help(self):
        """Verify init --help works."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize a Sentinel Scan configuration" in result.stdout

    def test_install_hook_help(self):
        """Verify install-hook --help works."""
        result = runner.invoke(app, ["install-hook", "--help"])
        assert result.exit_code == 0
        assert "Install a git hook" in result.stdout


class TestScanCommand:
    """Tests for scan command."""

    def test_scan_directory(self, tmp_path):
        """Verify scan command accepts directory."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\n")

        result = runner.invoke(app, ["scan", str(tmp_path)])
        # Currently just prints placeholder message
        assert result.exit_code == 0
        assert "Scanning" in result.stdout

    def test_scan_with_format(self, tmp_path):
        """Verify scan command accepts format option."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1\n")

        result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json"])
        assert result.exit_code == 0
        assert "Format: json" in result.stdout

    def test_scan_nonexistent_path(self):
        """Verify scan command handles nonexistent path."""
        result = runner.invoke(app, ["scan", "/nonexistent/path"])
        assert result.exit_code != 0
