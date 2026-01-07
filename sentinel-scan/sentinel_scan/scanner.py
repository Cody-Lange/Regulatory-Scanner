"""Scanner orchestrator for Sentinel Scan.

This module coordinates the scanning process:
- Loading and parsing files
- Running detectors
- Applying context analysis
- Aggregating results
"""

from pathlib import Path

from sentinel_scan.models import ScanResult


def scan_file(file_path: Path) -> ScanResult:
    """Scan a single file for compliance violations.

    Args:
        file_path: Path to the file to scan

    Returns:
        ScanResult with violations found in the file
    """
    # TODO: Implement in Phase 1
    return ScanResult(files_scanned=1, lines_scanned=0, violations=[])


def scan_directory(directory: Path, recursive: bool = True) -> ScanResult:
    """Scan a directory for compliance violations.

    Args:
        directory: Path to the directory to scan
        recursive: Whether to scan subdirectories

    Returns:
        ScanResult with violations found in all files
    """
    # TODO: Implement in Phase 1
    return ScanResult(files_scanned=0, lines_scanned=0, violations=[])
