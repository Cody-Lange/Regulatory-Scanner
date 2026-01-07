"""Data models for Sentinel Scan.

This module defines the core data structures used throughout the application:
- Severity: Enumeration of violation severity levels
- Violation: A single compliance violation detected in code
- ScanResult: Aggregated results from scanning files
- ScanContext: Context information for a scan operation
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any


class Severity(IntEnum):
    """Severity levels for compliance violations.

    Levels are ordered from least to most severe:
    - LOW: Informational, may be false positive or test data
    - MEDIUM: Potential issue, requires review
    - HIGH: Likely violation, should be fixed
    - CRITICAL: Definite violation, must be fixed immediately
    """

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    def __str__(self) -> str:
        """Return human-readable severity name."""
        return self.name


@dataclass(frozen=True, slots=True)
class Violation:
    """A single compliance violation detected in source code.

    Attributes:
        file_path: Absolute or relative path to the file containing the violation
        line_number: 1-indexed line number where the violation occurs
        column_number: 0-indexed column where the violation starts
        end_column: 0-indexed column where the violation ends
        detector: Name of the detector that found this violation (e.g., "pii", "vin")
        violation_type: Specific type of violation (e.g., "email", "ssn", "vin")
        matched_text: The text that triggered the violation (truncated for security)
        severity: How severe this violation is
        regulation: Relevant regulation (e.g., "GDPR Article 6", "CCPA")
        message: Human-readable description of the violation
        recommendation: Suggested fix for the violation
        context_info: Additional context (test file, LLM flow, etc.)
    """

    file_path: str
    line_number: int
    column_number: int
    end_column: int
    detector: str
    violation_type: str
    matched_text: str
    severity: Severity
    regulation: str
    message: str
    recommendation: str
    context_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert violation to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "end_column": self.end_column,
            "detector": self.detector,
            "violation_type": self.violation_type,
            "matched_text": self.matched_text,
            "severity": str(self.severity),
            "severity_level": int(self.severity),
            "regulation": self.regulation,
            "message": self.message,
            "recommendation": self.recommendation,
            "context_info": self.context_info,
        }


@dataclass(slots=True)
class ScanResult:
    """Aggregated results from scanning one or more files.

    Attributes:
        files_scanned: Number of files that were scanned
        lines_scanned: Total lines of code scanned
        violations: List of all violations found
        scan_duration_ms: Time taken to complete the scan in milliseconds
        timestamp: ISO format timestamp when the scan completed
        config_path: Path to the config file used (if any)
        errors: List of errors encountered during scanning
    """

    files_scanned: int = 0
    lines_scanned: int = 0
    violations: list[Violation] = field(default_factory=list)
    scan_duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    config_path: str | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def violation_count(self) -> int:
        """Total number of violations found."""
        return len(self.violations)

    @property
    def has_violations(self) -> bool:
        """Whether any violations were found."""
        return len(self.violations) > 0

    @property
    def critical_count(self) -> int:
        """Number of critical severity violations."""
        return sum(1 for v in self.violations if v.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Number of high severity violations."""
        return sum(1 for v in self.violations if v.severity == Severity.HIGH)

    def violations_by_severity(self, severity: Severity) -> list[Violation]:
        """Get all violations of a specific severity level."""
        return [v for v in self.violations if v.severity == severity]

    def violations_by_file(self) -> dict[str, list[Violation]]:
        """Group violations by file path."""
        result: dict[str, list[Violation]] = {}
        for violation in self.violations:
            if violation.file_path not in result:
                result[violation.file_path] = []
            result[violation.file_path].append(violation)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert scan result to dictionary for JSON serialization."""
        return {
            "files_scanned": self.files_scanned,
            "lines_scanned": self.lines_scanned,
            "violation_count": self.violation_count,
            "violations": [v.to_dict() for v in self.violations],
            "scan_duration_ms": self.scan_duration_ms,
            "timestamp": self.timestamp,
            "config_path": self.config_path,
            "errors": self.errors,
            "summary": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": sum(1 for v in self.violations if v.severity == Severity.MEDIUM),
                "low": sum(1 for v in self.violations if v.severity == Severity.LOW),
            },
        }


@dataclass(slots=True)
class ScanContext:
    """Context information for a scan operation.

    Attributes:
        is_test_file: Whether the current file is a test file
        is_in_test_function: Whether current location is inside a test function
        is_in_comment: Whether current location is in a comment
        is_in_docstring: Whether current location is in a docstring
        flows_to_llm_api: Whether the matched data flows to an LLM API call
        has_inline_ignore: Whether there's an inline ignore comment
        ignore_types: Specific violation types to ignore (from inline comment)
    """

    is_test_file: bool = False
    is_in_test_function: bool = False
    is_in_comment: bool = False
    is_in_docstring: bool = False
    flows_to_llm_api: bool = False
    has_inline_ignore: bool = False
    ignore_types: set[str] = field(default_factory=set)
