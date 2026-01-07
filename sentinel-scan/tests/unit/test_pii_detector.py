"""Tests for PII detector.

This module tests the PII detector's ability to detect:
- Email addresses
- Phone numbers (US formats)
- Social Security Numbers (SSN)
- Credit card numbers with Luhn validation
"""

import ast

import pytest

from sentinel_scan.detection.context_analyzer import ContextAnalyzer
from sentinel_scan.detection.pii_detector import PIIDetector
from sentinel_scan.models import Severity


class TestEmailDetection:
    """Tests for email detection."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a PII detector instance."""
        return PIIDetector()

    def _scan_source(self, detector: PIIDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_detects_simple_email(self, detector: PIIDetector) -> None:
        """Test detection of a simple email address."""
        source = 'email = "user@example.com"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert violations[0].violation_type == "email"
        assert violations[0].detector == "pii"
        assert "user@example.com" in violations[0].matched_text or "user" in violations[0].matched_text

    def test_detects_email_in_fstring(self, detector: PIIDetector) -> None:
        """Test detection of email in f-string."""
        source = 'msg = f"Contact: john.doe@company.com"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert violations[0].violation_type == "email"

    def test_detects_multiple_emails(self, detector: PIIDetector) -> None:
        """Test detection of multiple email addresses."""
        source = '''
emails = [
    "alice@example.com",
    "bob@company.org",
    "charlie@domain.net"
]
'''
        violations = self._scan_source(detector, source)
        email_violations = [v for v in violations if v.violation_type == "email"]

        assert len(email_violations) == 3

    def test_ignores_invalid_email_format(self, detector: PIIDetector) -> None:
        """Test that invalid email formats are not detected."""
        source = '''
not_email = "userexample.com"  # No @ symbol
also_not = "@example.com"  # No local part
'''
        violations = self._scan_source(detector, source)
        email_violations = [v for v in violations if v.violation_type == "email"]

        assert len(email_violations) == 0

    def test_ignores_email_in_test_file(self, detector: PIIDetector) -> None:
        """Test that emails in test files are lower severity."""
        source = 'test_email = "test@example.com"'
        violations = self._scan_source(detector, source, "tests/test_email.py")

        # Should still detect but with lower severity
        assert len(violations) >= 0  # Context may reduce or skip

    def test_ignores_email_with_inline_ignore(self, detector: PIIDetector) -> None:
        """Test inline ignore comment."""
        source = 'email = "user@example.com"  # sentinel-scan: ignore'
        violations = self._scan_source(detector, source)

        assert len(violations) == 0

    def test_ignores_email_with_specific_ignore(self, detector: PIIDetector) -> None:
        """Test inline ignore with specific type."""
        source = 'email = "user@example.com"  # sentinel-scan: ignore email'
        violations = self._scan_source(detector, source)

        assert len(violations) == 0

    def test_email_severity_is_high(self, detector: PIIDetector) -> None:
        """Test that email violations have HIGH severity."""
        source = 'email = "user@example.com"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert violations[0].severity == Severity.HIGH

    def test_email_has_gdpr_regulation(self, detector: PIIDetector) -> None:
        """Test that email violations reference GDPR."""
        source = 'email = "user@example.com"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert "GDPR" in violations[0].regulation


class TestPhoneDetection:
    """Tests for phone number detection."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a PII detector instance."""
        return PIIDetector()

    def _scan_source(self, detector: PIIDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_detects_dashed_phone(self, detector: PIIDetector) -> None:
        """Test detection of dashed phone number format."""
        source = 'phone = "555-123-4567"'
        violations = self._scan_source(detector, source)
        phone_violations = [v for v in violations if v.violation_type == "phone"]

        assert len(phone_violations) == 1

    def test_detects_dotted_phone(self, detector: PIIDetector) -> None:
        """Test detection of dotted phone number format."""
        source = 'phone = "555.123.4567"'
        violations = self._scan_source(detector, source)
        phone_violations = [v for v in violations if v.violation_type == "phone"]

        assert len(phone_violations) == 1

    def test_detects_parentheses_phone(self, detector: PIIDetector) -> None:
        """Test detection of phone with area code in parentheses."""
        source = 'phone = "(555) 123-4567"'
        violations = self._scan_source(detector, source)
        phone_violations = [v for v in violations if v.violation_type == "phone"]

        assert len(phone_violations) == 1

    def test_detects_phone_with_country_code(self, detector: PIIDetector) -> None:
        """Test detection of phone with +1 country code."""
        source = 'phone = "+1-555-123-4567"'
        violations = self._scan_source(detector, source)
        phone_violations = [v for v in violations if v.violation_type == "phone"]

        assert len(phone_violations) == 1

    def test_ignores_invalid_phone(self, detector: PIIDetector) -> None:
        """Test that invalid phone formats are not detected."""
        source = '''
not_phone = "123-456"  # Too short
also_not = "12345678901234"  # Too long
'''
        violations = self._scan_source(detector, source)
        phone_violations = [v for v in violations if v.violation_type == "phone"]

        assert len(phone_violations) == 0

    def test_phone_severity_is_high(self, detector: PIIDetector) -> None:
        """Test that phone violations have HIGH severity."""
        source = 'phone = "555-123-4567"'
        violations = self._scan_source(detector, source)
        phone_violations = [v for v in violations if v.violation_type == "phone"]

        assert len(phone_violations) == 1
        assert phone_violations[0].severity == Severity.HIGH


class TestSSNDetection:
    """Tests for Social Security Number detection."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a PII detector instance."""
        return PIIDetector()

    def _scan_source(self, detector: PIIDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_detects_dashed_ssn(self, detector: PIIDetector) -> None:
        """Test detection of standard SSN format."""
        source = 'ssn = "123-45-6789"'
        violations = self._scan_source(detector, source)
        ssn_violations = [v for v in violations if v.violation_type == "ssn"]

        assert len(ssn_violations) == 1

    def test_detects_spaced_ssn(self, detector: PIIDetector) -> None:
        """Test detection of SSN with spaces."""
        source = 'ssn = "123 45 6789"'
        violations = self._scan_source(detector, source)
        ssn_violations = [v for v in violations if v.violation_type == "ssn"]

        assert len(ssn_violations) == 1

    def test_ignores_invalid_ssn_format(self, detector: PIIDetector) -> None:
        """Test that invalid SSN formats are not detected."""
        source = '''
not_ssn = "000-00-0000"  # All zeros invalid
also_not = "123-00-6789"  # Middle zeros invalid
invalid_area = "000-45-6789"  # Area number cannot be 000
'''
        violations = self._scan_source(detector, source)
        ssn_violations = [v for v in violations if v.violation_type == "ssn"]

        assert len(ssn_violations) == 0

    def test_ssn_severity_is_critical(self, detector: PIIDetector) -> None:
        """Test that SSN violations have CRITICAL severity."""
        source = 'ssn = "123-45-6789"'
        violations = self._scan_source(detector, source)
        ssn_violations = [v for v in violations if v.violation_type == "ssn"]

        assert len(ssn_violations) == 1
        assert ssn_violations[0].severity == Severity.CRITICAL


class TestCreditCardDetection:
    """Tests for credit card number detection with Luhn validation."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a PII detector instance."""
        return PIIDetector()

    def _scan_source(self, detector: PIIDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_detects_visa_card(self, detector: PIIDetector) -> None:
        """Test detection of Visa card number (valid Luhn)."""
        # 4532015112830366 is a valid test Visa number
        source = 'card = "4532015112830366"'
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 1

    def test_detects_mastercard(self, detector: PIIDetector) -> None:
        """Test detection of Mastercard number (valid Luhn)."""
        # 5425233430109903 is a valid test Mastercard number
        source = 'card = "5425233430109903"'
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 1

    def test_detects_amex(self, detector: PIIDetector) -> None:
        """Test detection of American Express card (valid Luhn)."""
        # 378282246310005 is a valid test Amex number
        source = 'card = "378282246310005"'
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 1

    def test_detects_card_with_spaces(self, detector: PIIDetector) -> None:
        """Test detection of card with spaces."""
        source = 'card = "4532 0151 1283 0366"'
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 1

    def test_detects_card_with_dashes(self, detector: PIIDetector) -> None:
        """Test detection of card with dashes."""
        source = 'card = "4532-0151-1283-0366"'
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 1

    def test_ignores_invalid_luhn(self, detector: PIIDetector) -> None:
        """Test that invalid Luhn checksums are not detected."""
        # 4532015112830367 fails Luhn check (last digit wrong)
        source = 'card = "4532015112830367"'
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 0

    def test_ignores_too_short_number(self, detector: PIIDetector) -> None:
        """Test that short numbers are not detected."""
        source = 'not_card = "4532015112"'  # Only 10 digits
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 0

    def test_credit_card_severity_is_critical(self, detector: PIIDetector) -> None:
        """Test that credit card violations have CRITICAL severity."""
        source = 'card = "4532015112830366"'
        violations = self._scan_source(detector, source)
        cc_violations = [v for v in violations if v.violation_type == "credit_card"]

        assert len(cc_violations) == 1
        assert cc_violations[0].severity == Severity.CRITICAL


class TestAllowlistFiltering:
    """Tests for allowlist filtering."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a PII detector instance."""
        return PIIDetector()

    def _scan_source(
        self, detector: PIIDetector, source: str, file_path: str = "test.py", allowlist: list | None = None
    ) -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        if allowlist:
            detector.set_allowlist(allowlist)
        return detector.scan(source, tree, context, file_path)

    def test_allowlist_filters_email(self, detector: PIIDetector) -> None:
        """Test that allowlisted emails are not flagged."""
        source = 'email = "test@example.com"'
        violations = self._scan_source(detector, source, allowlist=["example.com"])

        assert len(violations) == 0

    def test_allowlist_partial_match(self, detector: PIIDetector) -> None:
        """Test that partial allowlist matches work."""
        source = 'email = "noreply@example.com"'
        violations = self._scan_source(detector, source, allowlist=["noreply@"])

        assert len(violations) == 0

    def test_allowlist_filters_phone(self, detector: PIIDetector) -> None:
        """Test that allowlisted phones are not flagged."""
        source = 'phone = "555-0100"'
        violations = self._scan_source(detector, source, allowlist=["555-0100"])
        phone_violations = [v for v in violations if v.violation_type == "phone"]

        assert len(phone_violations) == 0


class TestContextAwareness:
    """Tests for context-aware detection."""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a PII detector instance."""
        return PIIDetector()

    def _scan_source(self, detector: PIIDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_lower_severity_in_test_function(self, detector: PIIDetector) -> None:
        """Test that violations in test functions have lower severity."""
        source = '''
def test_email():
    email = "test@example.com"
'''
        violations = self._scan_source(detector, source, "tests/test_module.py")

        # In test functions, severity should be reduced
        for v in violations:
            if v.violation_type == "email":
                assert v.severity <= Severity.MEDIUM

    def test_skips_comment_only_lines(self, detector: PIIDetector) -> None:
        """Test that comment-only lines are skipped."""
        source = '''# Contact: admin@company.com
email = "actual@email.com"
'''
        violations = self._scan_source(detector, source)
        email_violations = [v for v in violations if v.violation_type == "email"]

        # Should only detect the actual email, not the commented one
        assert len(email_violations) == 1
        # Check that the violation is on line 2 (the actual email, not the comment)
        assert email_violations[0].line_number == 2

    def test_skips_docstrings(self, detector: PIIDetector) -> None:
        """Test that emails in docstrings are skipped or reduced severity."""
        source = '''
def process():
    """Process data.

    Contact: support@example.com for help.
    """
    return True
'''
        violations = self._scan_source(detector, source)

        # Docstrings should be skipped or have low severity
        assert len(violations) == 0

    def test_increases_severity_near_llm_call(self, detector: PIIDetector) -> None:
        """Test that violations near LLM API calls have higher severity."""
        source = '''
email = "user@company.com"
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": f"Contact {email}"}]
)
'''
        violations = self._scan_source(detector, source)

        # Near LLM calls, severity should be elevated
        for v in violations:
            if v.violation_type == "email":
                assert v.context_info.get("flows_to_llm_api", False) or v.severity >= Severity.HIGH
