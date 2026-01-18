"""Scanner orchestrator for Sentinel Scan.

This module coordinates the scanning process:
- Loading and parsing files
- Running detectors
- Applying context analysis
- Aggregating results
"""

import ast
import time
from pathlib import Path
from typing import TYPE_CHECKING

from sentinel_scan.config import Config, get_default_config
from sentinel_scan.detection.context_analyzer import ContextAnalyzer
from sentinel_scan.detection.registry import DetectorRegistry
from sentinel_scan.models import ScanResult, Severity, Violation

if TYPE_CHECKING:
    from sentinel_scan.detection.base import Detector

# Import detectors to register them
from sentinel_scan.detection import pii_detector, vin_detector  # noqa: F401


class Scanner:
    """Orchestrates the scanning process.

    Coordinates multiple detectors, applies context analysis,
    and aggregates results into a ScanResult.
    """

    def __init__(self, config: Config | None = None) -> None:
        """Initialize the scanner.

        Args:
            config: Configuration object. If None, uses defaults.
        """
        self.config = config or get_default_config()
        self.detectors: list[Detector] = self._initialize_detectors()

    def _initialize_detectors(self) -> list["Detector"]:
        """Initialize and configure all enabled detectors.

        Returns:
            List of configured detector instances
        """
        detectors = DetectorRegistry.create_all(
            {"detectors": self.config.detectors}
        )

        # Configure allowlists for each detector
        for detector in detectors:
            if hasattr(detector, "set_allowlist"):
                detector.set_allowlist(self.config.allowlist)

        return detectors

    def _parse_source(self, source: str) -> ast.AST | None:
        """Parse source code into AST.

        Args:
            source: Python source code

        Returns:
            Parsed AST or None if parsing fails
        """
        try:
            return ast.parse(source)
        except SyntaxError:
            return None

    def _filter_by_severity(self, violations: list[Violation]) -> list[Violation]:
        """Filter violations by minimum severity.

        Args:
            violations: List of violations to filter

        Returns:
            Filtered list of violations
        """
        severity_map = {
            "low": Severity.LOW,
            "medium": Severity.MEDIUM,
            "high": Severity.HIGH,
            "critical": Severity.CRITICAL,
        }

        min_severity = severity_map.get(
            self.config.settings.min_severity.lower(),
            Severity.LOW
        )

        return [v for v in violations if v.severity >= min_severity]

    def scan_source(self, source: str, file_path: str) -> ScanResult:
        """Scan source code for violations.

        Args:
            source: Python source code to scan
            file_path: Path to the file (for context)

        Returns:
            ScanResult with all violations found
        """
        start_time = time.perf_counter()
        violations: list[Violation] = []
        errors: list[str] = []

        # Parse the source
        tree = self._parse_source(source)
        if tree is None:
            # Create a dummy tree for detectors that don't need it
            try:
                tree = ast.parse("")
            except SyntaxError:
                tree = ast.Module(body=[], type_ignores=[])

        # Create context analyzer
        try:
            context = ContextAnalyzer(source, file_path)
        except Exception as e:
            errors.append(f"Context analysis failed: {e}")
            # Create minimal context
            context = ContextAnalyzer("", file_path)

        # Run each detector
        for detector in self.detectors:
            try:
                detector_violations = detector.scan(source, tree, context, file_path)
                violations.extend(detector_violations)
            except Exception as e:
                errors.append(f"Detector {detector.name} failed: {e}")

        # Filter by minimum severity
        violations = self._filter_by_severity(violations)

        # Calculate metrics
        lines_scanned = len(source.splitlines()) if source else 0
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        return ScanResult(
            files_scanned=1,
            lines_scanned=lines_scanned,
            violations=violations,
            scan_duration_ms=duration_ms,
            config_path=None,
            errors=errors,
        )


def scan_file(file_path: Path, config: Config | None = None) -> ScanResult:
    """Scan a single file for compliance violations.

    Args:
        file_path: Path to the file to scan
        config: Optional configuration

    Returns:
        ScanResult with violations found in the file
    """
    start_time = time.perf_counter()
    errors: list[str] = []

    # Check if file exists
    if not file_path.exists():
        return ScanResult(
            files_scanned=0,
            lines_scanned=0,
            violations=[],
            scan_duration_ms=0,
            errors=[f"File not found: {file_path}"],
        )

    # Read file content
    source = ""
    try:
        source = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1 for legacy files
            source = file_path.read_text(encoding="latin-1")
        except Exception as e:
            errors.append(f"Failed to read {file_path}: {e}")
            return ScanResult(
                files_scanned=0,
                lines_scanned=0,
                violations=[],
                scan_duration_ms=int((time.perf_counter() - start_time) * 1000),
                errors=errors,
            )
    except Exception as e:
        errors.append(f"Failed to read {file_path}: {e}")
        return ScanResult(
            files_scanned=0,
            lines_scanned=0,
            violations=[],
            scan_duration_ms=int((time.perf_counter() - start_time) * 1000),
            errors=errors,
        )

    # Create scanner and scan
    scanner = Scanner(config)
    result = scanner.scan_source(source, str(file_path))

    # Update the file path in violations to be absolute
    updated_violations = []
    for v in result.violations:
        updated_violations.append(
            Violation(
                file_path=str(file_path.resolve()),
                line_number=v.line_number,
                column_number=v.column_number,
                end_column=v.end_column,
                detector=v.detector,
                violation_type=v.violation_type,
                matched_text=v.matched_text,
                severity=v.severity,
                regulation=v.regulation,
                message=v.message,
                recommendation=v.recommendation,
                context_info=v.context_info,
            )
        )

    result.violations = updated_violations
    result.errors.extend(errors)

    return result


def scan_directory(
    directory: Path,
    recursive: bool = True,
    config: Config | None = None,
) -> ScanResult:
    """Scan a directory for compliance violations.

    Args:
        directory: Path to the directory to scan
        recursive: Whether to scan subdirectories
        config: Optional configuration

    Returns:
        ScanResult with violations found in all files
    """
    start_time = time.perf_counter()
    all_violations: list[Violation] = []
    all_errors: list[str] = []
    files_scanned = 0
    lines_scanned = 0

    # Check if directory exists
    if not directory.exists():
        return ScanResult(
            files_scanned=0,
            lines_scanned=0,
            violations=[],
            scan_duration_ms=0,
            errors=[f"Directory not found: {directory}"],
        )

    if not directory.is_dir():
        return ScanResult(
            files_scanned=0,
            lines_scanned=0,
            violations=[],
            scan_duration_ms=0,
            errors=[f"Not a directory: {directory}"],
        )

    # Get configuration for exclusions
    cfg = config or get_default_config()

    # Find Python files
    pattern = "**/*.py" if recursive else "*.py"
    python_files = list(directory.glob(pattern))

    for py_file in python_files:
        # Check exclusions
        file_str = str(py_file)
        excluded = False
        for exclusion in cfg.exclusions.paths:
            # Simple glob matching
            if _matches_pattern(file_str, exclusion):
                excluded = True
                break

        if excluded:
            continue

        # Scan the file
        result = scan_file(py_file, config)
        files_scanned += result.files_scanned
        lines_scanned += result.lines_scanned
        all_violations.extend(result.violations)
        all_errors.extend(result.errors)

    duration_ms = int((time.perf_counter() - start_time) * 1000)

    return ScanResult(
        files_scanned=files_scanned,
        lines_scanned=lines_scanned,
        violations=all_violations,
        scan_duration_ms=duration_ms,
        config_path=None,
        errors=all_errors,
    )


def _matches_pattern(path: str, pattern: str) -> bool:
    """Check if a path matches a glob-like pattern.

    Args:
        path: File path to check
        pattern: Glob pattern (supports * and **)

    Returns:
        True if path matches pattern
    """
    import fnmatch

    # Normalize pattern
    pattern = pattern.replace("\\", "/")
    path = path.replace("\\", "/")

    # Handle ** for recursive matching
    if "**" in pattern:
        # Split on **
        parts = pattern.split("**")
        if len(parts) == 2:
            start, end = parts
            start = start.rstrip("/")
            end = end.lstrip("/")

            if start and not path.startswith(start.replace("*", "")):
                return False
            return not (end and not fnmatch.fnmatch(path, f"*{end}"))

    return fnmatch.fnmatch(path, pattern)
