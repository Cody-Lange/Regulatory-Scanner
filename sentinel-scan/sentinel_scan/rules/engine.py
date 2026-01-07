"""Rule engine for Sentinel Scan.

This module applies rules to filter and process violations:
- Allowlist filtering
- Severity adjustments based on context
- Exclusion patterns
"""

import fnmatch
import re
from typing import Any

from sentinel_scan.models import Severity, Violation


class RuleEngine:
    """Engine for applying rules to violations.

    The rule engine takes raw violations and applies:
    1. Allowlist filtering (global and per-detector)
    2. Context-based severity adjustments
    3. Deduplication
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the rule engine with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.global_allowlist = config.get("allowlist", [])
        self.exclusion_paths = config.get("exclusions", {}).get("paths", [])

    def should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from scanning.

        Args:
            file_path: Path to check

        Returns:
            True if the file should be excluded
        """
        for pattern in self.exclusion_paths:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def is_allowlisted(self, matched_text: str, detector: str) -> bool:
        """Check if matched text is in the allowlist.

        Args:
            matched_text: The text that was matched
            detector: Name of the detector

        Returns:
            True if the text should be allowed (not flagged)
        """
        # Check global allowlist
        for pattern in self.global_allowlist:
            if pattern in matched_text:
                return True

        # Check detector-specific allowlist
        detector_config = self.config.get("detectors", {}).get(detector, {})
        detector_allowlist = detector_config.get("allowlist", [])

        for pattern in detector_allowlist:
            if pattern in matched_text:
                return True

        return False

    def adjust_severity(self, violation: Violation, is_test: bool, flows_to_llm: bool) -> Severity:
        """Adjust violation severity based on context.

        Args:
            violation: The violation to adjust
            is_test: Whether the violation is in test code
            flows_to_llm: Whether the data flows to an LLM API

        Returns:
            Adjusted severity level
        """
        severity = violation.severity

        # Lower severity for test code
        if is_test:
            return Severity.LOW

        # Elevate severity if data flows to LLM
        if flows_to_llm and severity == Severity.HIGH:
            return Severity.CRITICAL

        return severity

    def filter_violations(self, violations: list[Violation]) -> list[Violation]:
        """Filter violations through allowlists.

        Args:
            violations: List of violations to filter

        Returns:
            Filtered list of violations
        """
        filtered = []

        for violation in violations:
            # Skip if allowlisted
            if self.is_allowlisted(violation.matched_text, violation.detector):
                continue

            filtered.append(violation)

        return filtered

    def filter_by_severity(
        self, violations: list[Violation], min_severity: Severity
    ) -> list[Violation]:
        """Filter violations by minimum severity.

        Args:
            violations: List of violations to filter
            min_severity: Minimum severity to include

        Returns:
            Filtered list of violations
        """
        return [v for v in violations if v.severity >= min_severity]
