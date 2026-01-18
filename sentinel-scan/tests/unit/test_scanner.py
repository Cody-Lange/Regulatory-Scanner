"""Tests for the Scanner orchestrator.

This module tests the Scanner's ability to:
- Coordinate multiple detectors
- Apply context analysis
- Filter violations based on config
- Handle file encoding and errors
"""

import tempfile
from pathlib import Path

import pytest

from sentinel_scan.config import Settings, get_default_config
from sentinel_scan.models import Severity
from sentinel_scan.scanner import Scanner, scan_directory, scan_file


class TestScannerOrchestrator:
    """Tests for the Scanner class."""

    @pytest.fixture
    def scanner(self) -> Scanner:
        """Create a Scanner instance with default config."""
        config = get_default_config()
        config.allowlist = []  # Clear allowlist for testing
        return Scanner(config)

    def test_scanner_initializes_detectors(self, scanner: Scanner) -> None:
        """Test that scanner initializes all registered detectors."""
        assert len(scanner.detectors) >= 2  # At least PII and VIN

    def test_scanner_finds_pii_violations(self, scanner: Scanner) -> None:
        """Test that scanner detects PII violations."""
        source = """
email = "user@example.com"
phone = "555-123-4567"
"""
        result = scanner.scan_source(source, "test.py")

        assert result.has_violations
        assert result.violation_count >= 2

    def test_scanner_finds_vin_violations(self, scanner: Scanner) -> None:
        """Test that scanner detects VIN violations."""
        # Use a valid VIN with correct checksum
        source = 'vin = "5YJSA1DG9DFP14705"'
        result = scanner.scan_source(source, "test.py")

        assert result.has_violations
        vin_violations = [v for v in result.violations if v.violation_type == "vin"]
        assert len(vin_violations) == 1

    def test_scanner_counts_lines(self, scanner: Scanner) -> None:
        """Test that scanner correctly counts lines."""
        source = """line1
line2
line3
line4
line5
"""
        result = scanner.scan_source(source, "test.py")

        assert result.lines_scanned == 5

    def test_scanner_applies_context_analysis(self, scanner: Scanner) -> None:
        """Test that scanner applies context analysis."""
        source = '''
def test_email():
    """Test function with email."""
    email = "test@example.com"
'''
        result = scanner.scan_source(source, "tests/test_module.py")

        # Violations in test files should have reduced severity
        for v in result.violations:
            if v.violation_type == "email":
                assert v.severity <= Severity.MEDIUM

    def test_scanner_respects_inline_ignores(self, scanner: Scanner) -> None:
        """Test that scanner respects inline ignore comments."""
        source = 'email = "user@example.com"  # sentinel-scan: ignore'
        result = scanner.scan_source(source, "test.py")

        assert not result.has_violations

    def test_scanner_skips_docstrings(self, scanner: Scanner) -> None:
        """Test that scanner skips violations in docstrings."""
        source = '''
def process():
    """Contact: admin@example.com"""
    return True
'''
        result = scanner.scan_source(source, "test.py")

        assert not result.has_violations

    def test_scanner_handles_syntax_errors(self, scanner: Scanner) -> None:
        """Test that scanner handles files with syntax errors gracefully."""
        source = """
def broken(
    # Missing closing paren
email = "test@example.com"
"""
        result = scanner.scan_source(source, "test.py")

        # Should not crash, may have errors or limited detection
        assert result is not None


class TestScanFile:
    """Tests for scan_file function."""

    def test_scan_file_reads_python_file(self) -> None:
        """Test scanning a Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('email = "test@example.com"\n')
            f.flush()

            result = scan_file(Path(f.name))

            assert result.files_scanned == 1
            assert result.lines_scanned >= 1

    def test_scan_file_handles_nonexistent_file(self) -> None:
        """Test handling of nonexistent files."""
        result = scan_file(Path("/nonexistent/file.py"))

        assert result.files_scanned == 0
        assert len(result.errors) > 0

    def test_scan_file_handles_encoding_issues(self) -> None:
        """Test handling of files with encoding issues."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
            # Write invalid UTF-8
            f.write(b'email = "test@example.com"\n\xff\xfe')
            f.flush()

            result = scan_file(Path(f.name))

            # Should handle gracefully with fallback encoding
            assert result is not None


class TestScanDirectory:
    """Tests for scan_directory function."""

    def test_scan_directory_finds_python_files(self) -> None:
        """Test scanning a directory for Python files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text('email = "test@example.com"\n')

            result = scan_directory(Path(tmpdir))

            assert result.files_scanned >= 1

    def test_scan_directory_recursive(self) -> None:
        """Test recursive directory scanning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested directory with Python file
            nested = Path(tmpdir) / "nested"
            nested.mkdir()
            py_file = nested / "test.py"
            py_file.write_text('email = "test@example.com"\n')

            result = scan_directory(Path(tmpdir), recursive=True)

            assert result.files_scanned >= 1

    def test_scan_directory_handles_nonexistent(self) -> None:
        """Test handling of nonexistent directories."""
        result = scan_directory(Path("/nonexistent/directory"))

        assert result.files_scanned == 0
        assert len(result.errors) > 0


class TestScannerConfiguration:
    """Tests for scanner configuration."""

    def test_scanner_respects_detector_enabled(self) -> None:
        """Test that disabled detectors are not run."""
        config = get_default_config()
        config.detectors = {
            "pii": {"enabled": False},
            "vin": {"enabled": True},
        }
        scanner = Scanner(config)

        source = 'email = "test@example.com"'
        result = scanner.scan_source(source, "test.py")

        # PII detector disabled, so no email violations
        email_violations = [v for v in result.violations if v.violation_type == "email"]
        assert len(email_violations) == 0

    def test_scanner_respects_allowlist(self) -> None:
        """Test that allowlisted patterns are not flagged."""
        config = get_default_config()
        config.allowlist = ["example.com"]
        scanner = Scanner(config)

        source = 'email = "test@example.com"'
        result = scanner.scan_source(source, "test.py")

        assert not result.has_violations

    def test_scanner_respects_min_severity(self) -> None:
        """Test that violations below min severity are filtered."""
        config = get_default_config()
        config.settings = Settings(min_severity="high", exit_on_violation=True)
        config.allowlist = []
        scanner = Scanner(config)

        source = """
def test_email():
    email = "test@example.com"
"""
        result = scanner.scan_source(source, "tests/test_module.py")

        # Only HIGH or above should be reported
        for v in result.violations:
            assert v.severity >= Severity.HIGH


class TestScannerPerformance:
    """Tests for scanner performance characteristics."""

    def test_scanner_handles_large_file(self) -> None:
        """Test scanning a large file completes in reasonable time."""
        # Generate a 1000-line file
        lines = ['x = "value"'] * 1000
        lines[500] = (
            'email = "realuser@testdomain.org"'  # Add one violation (not in default allowlist)
        )
        source = "\n".join(lines)

        config = get_default_config()
        config.allowlist = []  # Clear allowlist before creating scanner
        scanner = Scanner(config)
        result = scanner.scan_source(source, "test.py")

        assert result.lines_scanned == 1000
        assert result.has_violations

    def test_scanner_handles_empty_file(self) -> None:
        """Test scanning an empty file."""
        scanner = Scanner(get_default_config())
        result = scanner.scan_source("", "test.py")

        assert result.lines_scanned == 0
        assert not result.has_violations
