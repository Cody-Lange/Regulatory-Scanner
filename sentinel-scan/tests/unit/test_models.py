"""Unit tests for data models."""

import pytest

from sentinel_scan.models import ScanContext, ScanResult, Severity, Violation


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_ordering(self):
        """Verify severity levels are ordered correctly."""
        assert Severity.LOW < Severity.MEDIUM
        assert Severity.MEDIUM < Severity.HIGH
        assert Severity.HIGH < Severity.CRITICAL

    def test_severity_values(self):
        """Verify severity integer values."""
        assert int(Severity.LOW) == 1
        assert int(Severity.MEDIUM) == 2
        assert int(Severity.HIGH) == 3
        assert int(Severity.CRITICAL) == 4

    def test_severity_str(self):
        """Verify severity string representation."""
        assert str(Severity.LOW) == "LOW"
        assert str(Severity.CRITICAL) == "CRITICAL"


class TestViolation:
    """Tests for Violation dataclass."""

    def test_violation_creation(self, sample_violation: Violation):
        """Verify violation can be created with all fields."""
        assert sample_violation.file_path == "src/example.py"
        assert sample_violation.line_number == 10
        assert sample_violation.detector == "pii"
        assert sample_violation.severity == Severity.HIGH

    def test_violation_immutable(self, sample_violation: Violation):
        """Verify violation is immutable (frozen)."""
        with pytest.raises(AttributeError):
            sample_violation.line_number = 20  # type: ignore

    def test_violation_to_dict(self, sample_violation: Violation):
        """Verify violation can be converted to dict."""
        d = sample_violation.to_dict()

        assert d["file_path"] == "src/example.py"
        assert d["line_number"] == 10
        assert d["severity"] == "HIGH"
        assert d["severity_level"] == 3


class TestScanResult:
    """Tests for ScanResult dataclass."""

    def test_scan_result_creation(self, sample_scan_result: ScanResult):
        """Verify scan result can be created."""
        assert sample_scan_result.files_scanned == 5
        assert sample_scan_result.lines_scanned == 500
        assert len(sample_scan_result.violations) == 1

    def test_violation_count(self, sample_scan_result: ScanResult):
        """Verify violation count property."""
        assert sample_scan_result.violation_count == 1

    def test_has_violations(
        self, sample_scan_result: ScanResult, empty_scan_result: ScanResult
    ):
        """Verify has_violations property."""
        assert sample_scan_result.has_violations is True
        assert empty_scan_result.has_violations is False

    def test_critical_count(self):
        """Verify critical count calculation."""
        violations = [
            Violation(
                file_path="test.py",
                line_number=1,
                column_number=0,
                end_column=10,
                detector="pii",
                violation_type="ssn",
                matched_text="***",
                severity=Severity.CRITICAL,
                regulation="CCPA",
                message="SSN detected",
                recommendation="Remove SSN",
            ),
            Violation(
                file_path="test.py",
                line_number=2,
                column_number=0,
                end_column=10,
                detector="pii",
                violation_type="email",
                matched_text="***",
                severity=Severity.HIGH,
                regulation="GDPR",
                message="Email detected",
                recommendation="Remove email",
            ),
        ]
        result = ScanResult(violations=violations)

        assert result.critical_count == 1
        assert result.high_count == 1

    def test_violations_by_file(self):
        """Verify violations can be grouped by file."""
        violations = [
            Violation(
                file_path="a.py",
                line_number=1,
                column_number=0,
                end_column=10,
                detector="pii",
                violation_type="email",
                matched_text="***",
                severity=Severity.HIGH,
                regulation="GDPR",
                message="Email",
                recommendation="Fix",
            ),
            Violation(
                file_path="b.py",
                line_number=1,
                column_number=0,
                end_column=10,
                detector="pii",
                violation_type="phone",
                matched_text="***",
                severity=Severity.HIGH,
                regulation="GDPR",
                message="Phone",
                recommendation="Fix",
            ),
            Violation(
                file_path="a.py",
                line_number=5,
                column_number=0,
                end_column=10,
                detector="pii",
                violation_type="ssn",
                matched_text="***",
                severity=Severity.CRITICAL,
                regulation="CCPA",
                message="SSN",
                recommendation="Fix",
            ),
        ]
        result = ScanResult(violations=violations)
        by_file = result.violations_by_file()

        assert len(by_file) == 2
        assert len(by_file["a.py"]) == 2
        assert len(by_file["b.py"]) == 1

    def test_to_dict(self, sample_scan_result: ScanResult):
        """Verify scan result can be converted to dict."""
        d = sample_scan_result.to_dict()

        assert d["files_scanned"] == 5
        assert d["violation_count"] == 1
        assert "summary" in d
        assert d["summary"]["high"] == 1


class TestScanContext:
    """Tests for ScanContext dataclass."""

    def test_default_context(self):
        """Verify default context values."""
        ctx = ScanContext()

        assert ctx.is_test_file is False
        assert ctx.is_in_test_function is False
        assert ctx.is_in_comment is False
        assert ctx.flows_to_llm_api is False
        assert ctx.has_inline_ignore is False
        assert len(ctx.ignore_types) == 0

    def test_custom_context(self):
        """Verify context can be customized."""
        ctx = ScanContext(
            is_test_file=True, is_in_test_function=True, ignore_types={"email", "phone"}
        )

        assert ctx.is_test_file is True
        assert ctx.is_in_test_function is True
        assert "email" in ctx.ignore_types
