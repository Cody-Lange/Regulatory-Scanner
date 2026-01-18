"""PII (Personally Identifiable Information) detector for Sentinel Scan.

This module detects various types of PII in source code:
- Email addresses
- Phone numbers (US formats)
- Social Security Numbers (SSN)
- Credit card numbers (with Luhn validation)
"""

import ast
import re
from typing import TYPE_CHECKING

from sentinel_scan.detection.base import Detector
from sentinel_scan.detection.registry import DetectorRegistry
from sentinel_scan.models import Severity, Violation

if TYPE_CHECKING:
    from sentinel_scan.detection.context_analyzer import ContextAnalyzer


# Email pattern - standard email format validation
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Phone patterns - various US formats
PHONE_PATTERNS = [
    # (555) 123-4567 or (555)123-4567
    re.compile(r"\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b"),
    # 555-123-4567 or 555.123.4567 or 555 123 4567
    re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),
    # +1-555-123-4567 or +1 555 123 4567
    re.compile(r"\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
]

# SSN pattern - XXX-XX-XXXX format with validation
SSN_PATTERN = re.compile(r"\b(?!000|666|9\d{2})(\d{3})[-\s](?!00)(\d{2})[-\s](?!0000)(\d{4})\b")

# Credit card patterns - various formats (13-19 digits)
CREDIT_CARD_PATTERNS = [
    # Continuous digits (13-19 digits)
    re.compile(r"\b[3-6]\d{12,18}\b"),
    # With spaces (groups of 4)
    re.compile(r"\b[3-6]\d{3}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b"),
    # Amex format (15 digits: 4-6-5)
    re.compile(r"\b3[47]\d{2}[\s-]?\d{6}[\s-]?\d{5}\b"),
]


def luhn_checksum(card_number: str) -> bool:
    """Validate credit card number using Luhn algorithm.

    Args:
        card_number: Credit card number (digits only)

    Returns:
        True if valid Luhn checksum, False otherwise
    """
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13:
        return False

    # Reverse and process
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0


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


@DetectorRegistry.register("pii")
class PIIDetector(Detector):
    """Detector for Personally Identifiable Information.

    Detects emails, phone numbers, SSNs, and credit card numbers
    with context-aware severity adjustment.
    """

    def __init__(self) -> None:
        """Initialize the PII detector."""
        self._allowlist: list[str] = []

    @property
    def name(self) -> str:
        """Return detector name."""
        return "pii"

    def set_allowlist(self, patterns: list[str]) -> None:
        """Set allowlist patterns.

        Args:
            patterns: List of patterns to allowlist
        """
        self._allowlist = patterns

    def _is_allowlisted(self, text: str) -> bool:
        """Check if text matches any allowlist pattern.

        Args:
            text: Text to check

        Returns:
            True if allowlisted, False otherwise
        """
        return any(pattern in text for pattern in self._allowlist)

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

    def _should_skip(
        self, context: "ContextAnalyzer", line_number: int, violation_type: str
    ) -> bool:
        """Determine if a violation should be skipped based on context.

        Args:
            context: Context analyzer instance
            line_number: Line number to check
            violation_type: Type of violation (email, phone, etc.)

        Returns:
            True if violation should be skipped
        """
        scan_context = context.get_context(line_number)

        # Skip if inline ignore comment
        if scan_context.has_inline_ignore:
            # If no specific types, ignore all
            if not scan_context.ignore_types:
                return True
            # If specific types, check if this type should be ignored
            if violation_type.lower() in scan_context.ignore_types:
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
        violation_type: str,
        matched_text: str,
        severity: Severity,
        context: "ContextAnalyzer",
    ) -> Violation:
        """Create a violation object.

        Args:
            file_path: Path to the file
            line_number: Line number of violation
            column: Starting column
            end_column: Ending column
            violation_type: Type of PII detected
            matched_text: The matched text
            severity: Severity level
            context: Context analyzer

        Returns:
            Violation object
        """
        regulation_map = {
            "email": "GDPR Article 6, CCPA",
            "phone": "GDPR Article 6, CCPA",
            "ssn": "CCPA, State Privacy Laws",
            "credit_card": "PCI-DSS, CCPA",
        }

        message_map = {
            "email": "Email address detected in source code",
            "phone": "Phone number detected in source code",
            "ssn": "Social Security Number detected in source code",
            "credit_card": "Credit card number detected in source code",
        }

        recommendation_map = {
            "email": "Hash or remove email before sending to LLM. Use environment variables for configuration.",
            "phone": "Mask or remove phone number before sending to LLM. Use tokenization if needed.",
            "ssn": "CRITICAL: Remove SSN immediately. Never include in LLM prompts. Use secure tokenization.",
            "credit_card": "CRITICAL: Remove card number immediately. Never include in LLM prompts. Use payment tokens.",
        }

        scan_context = context.get_context(line_number)

        return Violation(
            file_path=file_path,
            line_number=line_number,
            column_number=column,
            end_column=end_column,
            detector=self.name,
            violation_type=violation_type,
            matched_text=truncate_matched_text(matched_text),
            severity=severity,
            regulation=regulation_map.get(violation_type, "GDPR, CCPA"),
            message=message_map.get(violation_type, f"{violation_type} detected"),
            recommendation=recommendation_map.get(
                violation_type, "Review and remove sensitive data"
            ),
            context_info={
                "is_test_file": scan_context.is_test_file,
                "is_in_test_function": scan_context.is_in_test_function,
                "flows_to_llm_api": scan_context.flows_to_llm_api,
            },
        )

    def _detect_emails(
        self,
        source: str,
        context: "ContextAnalyzer",
        file_path: str,
    ) -> list[Violation]:
        """Detect email addresses in source code.

        Args:
            source: Source code to scan
            context: Context analyzer
            file_path: Path to the file

        Returns:
            List of violations for detected emails
        """
        violations = []
        lines = source.splitlines()

        for line_num, line in enumerate(lines, start=1):
            for match in EMAIL_PATTERN.finditer(line):
                email = match.group(0)

                if self._is_allowlisted(email):
                    continue

                if self._should_skip(context, line_num, "email"):
                    continue

                severity = self._adjust_severity(Severity.HIGH, context, line_num)

                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start(),
                        end_column=match.end(),
                        violation_type="email",
                        matched_text=email,
                        severity=severity,
                        context=context,
                    )
                )

        return violations

    def _detect_phones(
        self,
        source: str,
        context: "ContextAnalyzer",
        file_path: str,
    ) -> list[Violation]:
        """Detect phone numbers in source code.

        Args:
            source: Source code to scan
            context: Context analyzer
            file_path: Path to the file

        Returns:
            List of violations for detected phone numbers
        """
        violations = []
        lines = source.splitlines()

        for line_num, line in enumerate(lines, start=1):
            # Track covered ranges to avoid overlapping matches
            covered_ranges: list[tuple[int, int]] = []

            for pattern in PHONE_PATTERNS:
                for match in pattern.finditer(line):
                    phone = match.group(0)
                    start, end = match.start(), match.end()

                    # Check if this match overlaps with any already covered range
                    is_overlapping = any(
                        not (end <= cov_start or start >= cov_end)
                        for cov_start, cov_end in covered_ranges
                    )

                    if is_overlapping:
                        continue

                    if self._is_allowlisted(phone):
                        continue

                    if self._should_skip(context, line_num, "phone"):
                        continue

                    severity = self._adjust_severity(Severity.HIGH, context, line_num)

                    violations.append(
                        self._create_violation(
                            file_path=file_path,
                            line_number=line_num,
                            column=start,
                            end_column=end,
                            violation_type="phone",
                            matched_text=phone,
                            severity=severity,
                            context=context,
                        )
                    )

                    # Mark this range as covered
                    covered_ranges.append((start, end))

        return violations

    def _detect_ssns(
        self,
        source: str,
        context: "ContextAnalyzer",
        file_path: str,
    ) -> list[Violation]:
        """Detect Social Security Numbers in source code.

        Args:
            source: Source code to scan
            context: Context analyzer
            file_path: Path to the file

        Returns:
            List of violations for detected SSNs
        """
        violations = []
        lines = source.splitlines()

        for line_num, line in enumerate(lines, start=1):
            for match in SSN_PATTERN.finditer(line):
                ssn = match.group(0)

                if self._is_allowlisted(ssn):
                    continue

                if self._should_skip(context, line_num, "ssn"):
                    continue

                # SSN is always CRITICAL severity (context can't lower it)
                severity = Severity.CRITICAL

                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start(),
                        end_column=match.end(),
                        violation_type="ssn",
                        matched_text=ssn,
                        severity=severity,
                        context=context,
                    )
                )

        return violations

    def _detect_credit_cards(
        self,
        source: str,
        context: "ContextAnalyzer",
        file_path: str,
    ) -> list[Violation]:
        """Detect credit card numbers in source code.

        Args:
            source: Source code to scan
            context: Context analyzer
            file_path: Path to the file

        Returns:
            List of violations for detected credit card numbers
        """
        violations = []
        lines = source.splitlines()
        seen_positions: set[tuple[int, int]] = set()  # Track (line, start) to avoid duplicates

        for line_num, line in enumerate(lines, start=1):
            for pattern in CREDIT_CARD_PATTERNS:
                for match in pattern.finditer(line):
                    card = match.group(0)
                    position = (line_num, match.start())

                    # Skip if we've already found a match at this position
                    if position in seen_positions:
                        continue

                    # Extract digits for Luhn validation
                    digits_only = "".join(c for c in card if c.isdigit())

                    # Validate with Luhn algorithm
                    if not luhn_checksum(digits_only):
                        continue

                    if self._is_allowlisted(card):
                        continue

                    if self._should_skip(context, line_num, "credit_card"):
                        continue

                    seen_positions.add(position)

                    # Credit card is always CRITICAL severity
                    severity = Severity.CRITICAL

                    violations.append(
                        self._create_violation(
                            file_path=file_path,
                            line_number=line_num,
                            column=match.start(),
                            end_column=match.end(),
                            violation_type="credit_card",
                            matched_text=card,
                            severity=severity,
                            context=context,
                        )
                    )

        return violations

    def scan(
        self,
        source: str,
        tree: ast.AST,  # noqa: ARG002 - Required by Detector interface
        context: "ContextAnalyzer",
        file_path: str,
    ) -> list[Violation]:
        """Scan source code for PII violations.

        Args:
            source: Source code to scan
            tree: Parsed AST (not used directly, but available for future use)
            context: Context analyzer for determining code context
            file_path: Path to the file being scanned

        Returns:
            List of PII violations found
        """
        violations = []

        violations.extend(self._detect_emails(source, context, file_path))
        violations.extend(self._detect_phones(source, context, file_path))
        violations.extend(self._detect_ssns(source, context, file_path))
        violations.extend(self._detect_credit_cards(source, context, file_path))

        return violations
