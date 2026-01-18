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


class TestScannerErrorHandling:
    """Tests for scanner error handling."""

    def test_scanner_handles_context_analyzer_exception(self, monkeypatch) -> None:
        """Test that scanner handles ContextAnalyzer exceptions gracefully."""
        from sentinel_scan.detection import context_analyzer

        original_init = context_analyzer.ContextAnalyzer.__init__

        def failing_init(self, source, file_path):
            if source and "trigger_error" in source:
                raise RuntimeError("Simulated context analysis failure")
            return original_init(self, source, file_path)

        monkeypatch.setattr(context_analyzer.ContextAnalyzer, "__init__", failing_init)

        config = get_default_config()
        config.allowlist = []
        scanner = Scanner(config)

        source = 'email = "test@example.com"  # trigger_error'
        result = scanner.scan_source(source, "test.py")

        # Should not crash, should have error recorded
        assert result is not None
        assert len(result.errors) > 0
        assert "Context analysis failed" in result.errors[0]

    def test_scanner_handles_detector_exception(self, monkeypatch) -> None:
        """Test that scanner handles detector exceptions gracefully."""
        from sentinel_scan.detection import pii_detector

        def failing_scan(_self, _source, _tree, _context, _file_path):
            raise RuntimeError("Simulated detector failure")

        monkeypatch.setattr(pii_detector.PIIDetector, "scan", failing_scan)

        config = get_default_config()
        config.allowlist = []
        scanner = Scanner(config)

        source = 'email = "test@example.com"'
        result = scanner.scan_source(source, "test.py")

        # Should not crash, should have error recorded
        assert result is not None
        assert len(result.errors) > 0
        assert "Detector" in result.errors[0] and "failed" in result.errors[0]


class TestScanFileEdgeCases:
    """Tests for scan_file edge cases."""

    def test_scan_file_with_violations_updates_path(self) -> None:
        """Test that scan_file updates file paths in violations to absolute."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('email = "realuser@testdomain.org"\n')
            f.flush()

            config = get_default_config()
            config.allowlist = []
            result = scan_file(Path(f.name), config)

            assert result.has_violations
            for v in result.violations:
                assert Path(v.file_path).is_absolute()

    def test_scan_file_with_permission_error(self, monkeypatch) -> None:
        """Test handling of files that can't be read due to permissions."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('email = "test@example.com"\n')
            f.flush()
            path = Path(f.name)

        # Mock read_text to raise PermissionError
        def mock_read_text(*_args, **_kwargs):
            raise PermissionError("Permission denied")

        monkeypatch.setattr(Path, "read_text", mock_read_text)

        result = scan_file(path)

        assert result.files_scanned == 0
        assert len(result.errors) > 0
        assert "Permission denied" in result.errors[0]

    def test_scan_file_latin1_fallback_works(self) -> None:
        """Test that latin-1 fallback works for non-UTF-8 files."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
            # Write valid latin-1 that's not valid UTF-8
            # \xe9 is 'é' in latin-1
            f.write(b'email = "test@example.com"  # caf\xe9\n')
            f.flush()

            result = scan_file(Path(f.name))

            # Should handle with latin-1 fallback, no errors
            assert result.files_scanned == 1


class TestScanDirectoryEdgeCases:
    """Tests for scan_directory edge cases."""

    def test_scan_directory_with_file_path(self) -> None:
        """Test scanning a file path instead of directory."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('email = "test@example.com"\n')
            f.flush()

            result = scan_directory(Path(f.name))

            assert result.files_scanned == 0
            assert len(result.errors) > 0
            assert "Not a directory" in result.errors[0]

    def test_scan_directory_with_exclusions(self) -> None:
        """Test that exclusion patterns work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files that should and shouldn't be excluded
            tests_dir = Path(tmpdir) / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "test_module.py"
            test_file.write_text('email = "test@example.com"\n')

            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            src_file = src_dir / "main.py"
            src_file.write_text('email = "realuser@testdomain.org"\n')

            config = get_default_config()
            config.allowlist = []
            config.exclusions.paths = ["*/tests/*"]

            result = scan_directory(Path(tmpdir), config=config)

            # Only src file should be scanned (tests excluded)
            assert result.files_scanned == 1


class TestMatchesPattern:
    """Tests for the _matches_pattern helper function."""

    def test_matches_simple_pattern(self) -> None:
        """Test simple glob pattern matching."""
        from sentinel_scan.scanner import _matches_pattern

        assert _matches_pattern("/path/to/test.py", "*.py")
        assert not _matches_pattern("/path/to/test.txt", "*.py")

    def test_matches_double_star_pattern(self) -> None:
        """Test ** glob pattern for recursive matching."""
        from sentinel_scan.scanner import _matches_pattern

        # Pattern with ** splits into start and end parts
        assert _matches_pattern("/project/tests/unit/test_foo.py", "**/test_foo.py")
        assert _matches_pattern("/project/tests/test_bar.py", "*/tests/*")

    def test_matches_double_star_with_suffix(self) -> None:
        """Test ** pattern with suffix matching."""
        from sentinel_scan.scanner import _matches_pattern

        # Test the actual behavior of ** patterns
        assert _matches_pattern("/project/.venv/lib/python/site.py", "**/*.py")
        assert _matches_pattern("/project/tests/unit/test_foo.py", "**/test_*.py")

    def test_matches_pattern_normalizes_slashes(self) -> None:
        """Test that pattern matching normalizes Windows-style slashes."""
        from sentinel_scan.scanner import _matches_pattern

        # Should handle both forward and backslashes
        assert _matches_pattern("C:\\Users\\test\\file.py", "*/test/*")

    def test_double_star_pattern_with_start_filter(self) -> None:
        """Test ** pattern with start path filter."""
        from sentinel_scan.scanner import _matches_pattern

        # Pattern like "tests/**" should only match paths starting with "tests"
        assert _matches_pattern("tests/unit/test_foo.py", "tests/**")
        assert not _matches_pattern("src/tests/test_foo.py", "tests/**")


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
