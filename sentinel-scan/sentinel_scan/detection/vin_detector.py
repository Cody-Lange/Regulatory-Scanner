"""VIN (Vehicle Identification Number) detector for Sentinel Scan.

This module detects Vehicle Identification Numbers in source code.
VINs are 17-character alphanumeric codes that uniquely identify vehicles.
"""

import ast
import re
from typing import TYPE_CHECKING

from sentinel_scan.detection.base import Detector
from sentinel_scan.detection.registry import DetectorRegistry
from sentinel_scan.models import Severity, Violation

if TYPE_CHECKING:
    from sentinel_scan.detection.context_analyzer import ContextAnalyzer


# VIN pattern - 17 alphanumeric characters, excluding I, O, Q
VIN_PATTERN = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")

# Character transliteration values for VIN checksum
VIN_TRANSLITERATION = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "J": 1,
    "K": 2,
    "L": 3,
    "M": 4,
    "N": 5,
    "P": 7,
    "R": 9,
    "S": 2,
    "T": 3,
    "U": 4,
    "V": 5,
    "W": 6,
    "X": 7,
    "Y": 8,
    "Z": 9,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}

# Position weights for VIN checksum calculation
VIN_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]


def calculate_vin_checksum(vin: str) -> str | None:
    """Calculate the check digit for a VIN.

    The VIN check digit is the 9th character and is calculated using
    a weighted sum of the transliterated values of all other characters.

    Args:
        vin: 17-character VIN string

    Returns:
        The expected check digit character, or None if VIN is invalid
    """
    if len(vin) != 17:
        return None

    vin = vin.upper()

    # Check for invalid characters (I, O, Q not allowed in VINs)
    if any(c in vin for c in "IOQ"):
        return None

    total = 0
    for i, char in enumerate(vin):
        if char not in VIN_TRANSLITERATION:
            return None
        value = VIN_TRANSLITERATION[char]
        total += value * VIN_WEIGHTS[i]

    remainder = total % 11
    if remainder == 10:
        return "X"
    return str(remainder)


def validate_vin_checksum(vin: str) -> bool:
    """Validate a VIN's check digit.

    Args:
        vin: 17-character VIN string

    Returns:
        True if the check digit is valid, False otherwise
    """
    if len(vin) != 17:
        return False

    vin = vin.upper()
    expected_check = calculate_vin_checksum(vin)

    if expected_check is None:
        return False

    # Check digit is the 9th character (index 8)
    actual_check = vin[8]
    return actual_check == expected_check


def truncate_matched_text(text: str) -> str:
    """Truncate matched text for security (show only first 4 and last 4 chars).

    Args:
        text: The matched sensitive text

    Returns:
        Truncated text with middle replaced by '...'
    """
    if len(text) <= 8:
        return text[:2] + "..." + text[-2:]
    return text[:4] + "..." + text[-4:]


@DetectorRegistry.register("vin")
class VINDetector(Detector):
    """Detector for Vehicle Identification Numbers.

    Detects 17-character VINs with optional checksum validation.
    VINs are considered sensitive in automotive contexts as they
    can be used to track vehicle ownership and history.
    """

    def __init__(self, validate_checksum: bool = True) -> None:
        """Initialize the VIN detector.

        Args:
            validate_checksum: Whether to validate VIN checksum (default True)
        """
        self._validate_checksum = validate_checksum
        self._allowlist: list[str] = []

    @property
    def name(self) -> str:
        """Return detector name."""
        return "vin"

    def set_allowlist(self, patterns: list[str]) -> None:
        """Set allowlist patterns.

        Args:
            patterns: List of VINs or prefixes to allowlist
        """
        self._allowlist = patterns

    def _is_allowlisted(self, vin: str) -> bool:
        """Check if VIN matches any allowlist pattern.

        Args:
            vin: VIN to check

        Returns:
            True if allowlisted, False otherwise
        """
        vin_upper = vin.upper()
        for pattern in self._allowlist:
            pattern_upper = pattern.upper()
            if vin_upper == pattern_upper or vin_upper.startswith(pattern_upper):
                return True
        return False

    def _adjust_severity(
        self,
        base_severity: Severity,
        context: "ContextAnalyzer",
        line_number: int,
    ) -> Severity:
        """Adjust severity based on context.

        Args:
            base_severity: The default severity level
            context: Context analyzer instance
            line_number: Line number of the violation

        Returns:
            Adjusted severity level
        """
        scan_context = context.get_context(line_number)

        # Test files/functions get reduced severity
        if (
            scan_context.is_test_file or scan_context.is_in_test_function
        ) and base_severity > Severity.LOW:
            return Severity(base_severity - 1)

        # Near LLM calls, elevate severity
        if scan_context.flows_to_llm_api and base_severity < Severity.CRITICAL:
            return Severity(base_severity + 1)

        return base_severity

    def _should_skip(self, context: "ContextAnalyzer", line_number: int) -> bool:
        """Determine if a violation should be skipped based on context.

        Args:
            context: Context analyzer instance
            line_number: Line number to check

        Returns:
            True if violation should be skipped
        """
        scan_context = context.get_context(line_number)

        # Skip if inline ignore comment
        if scan_context.has_inline_ignore:
            # If no specific types, ignore all
            if not scan_context.ignore_types:
                return True
            # If specific types, check if VIN should be ignored
            if "vin" in scan_context.ignore_types:
                return True

        # Skip comment-only lines
        if scan_context.is_in_comment:
            return True

        # Skip docstrings
        return bool(scan_context.is_in_docstring)

    def _create_violation(
        self,
        file_path: str,
        line_number: int,
        column: int,
        end_column: int,
        matched_text: str,
        severity: Severity,
        context: "ContextAnalyzer",
        checksum_valid: bool,
    ) -> Violation:
        """Create a violation object for a detected VIN.

        Args:
            file_path: Path to the file
            line_number: Line number of violation
            column: Starting column
            end_column: Ending column
            matched_text: The matched VIN
            severity: Severity level
            context: Context analyzer
            checksum_valid: Whether the VIN checksum is valid

        Returns:
            Violation object
        """
        scan_context = context.get_context(line_number)

        return Violation(
            file_path=file_path,
            line_number=line_number,
            column_number=column,
            end_column=end_column,
            detector=self.name,
            violation_type="vin",
            matched_text=truncate_matched_text(matched_text),
            severity=severity,
            regulation="GDPR Article 6, CCPA, Automotive Privacy Laws",
            message="Vehicle Identification Number (VIN) detected in source code",
            recommendation="Remove or hash VIN before sending to LLM. Use tokenization for vehicle lookups.",
            context_info={
                "is_test_file": scan_context.is_test_file,
                "is_in_test_function": scan_context.is_in_test_function,
                "flows_to_llm_api": scan_context.flows_to_llm_api,
                "checksum_valid": checksum_valid,
            },
        )

    def scan(
        self,
        source: str,
        tree: ast.AST,  # noqa: ARG002 - Required by Detector interface
        context: "ContextAnalyzer",
        file_path: str,
    ) -> list[Violation]:
        """Scan source code for VIN violations.

        Args:
            source: Source code to scan
            tree: Parsed AST (not used directly)
            context: Context analyzer for determining code context
            file_path: Path to the file being scanned

        Returns:
            List of VIN violations found
        """
        violations = []
        lines = source.splitlines()

        for line_num, line in enumerate(lines, start=1):
            for match in VIN_PATTERN.finditer(line):
                vin = match.group(0)

                # Validate checksum if enabled
                checksum_valid = validate_vin_checksum(vin)

                if self._validate_checksum and not checksum_valid:
                    continue

                if self._is_allowlisted(vin):
                    continue

                if self._should_skip(context, line_num):
                    continue

                severity = self._adjust_severity(Severity.HIGH, context, line_num)

                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start(),
                        end_column=match.end(),
                        matched_text=vin,
                        severity=severity,
                        context=context,
                        checksum_valid=checksum_valid,
                    )
                )

        return violations
