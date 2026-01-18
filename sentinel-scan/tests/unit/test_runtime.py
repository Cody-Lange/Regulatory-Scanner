"""Tests for runtime LLM protection.

Tests the ability to detect PII in data being sent to LLM APIs at runtime.
"""

import pytest

from sentinel_scan.runtime import (
    PIIDetectedError,
    RuntimeScanner,
    scan_llm_input,
    scan_payload,
)


class TestRuntimeScanner:
    """Tests for RuntimeScanner class."""

    def test_detects_email_in_string(self) -> None:
        """Test that scanner detects email addresses."""
        scanner = RuntimeScanner(block=False)
        result = scanner.scan("Contact john.doe@company.com for help")

        assert result.has_violations
        assert any(v.violation_type == "email" for v in result.violations)

    def test_detects_ssn_in_string(self) -> None:
        """Test that scanner detects SSNs."""
        scanner = RuntimeScanner(block=False)
        result = scanner.scan("My SSN is 123-45-6789")

        assert result.has_violations
        assert any(v.violation_type == "ssn" for v in result.violations)

    def test_detects_phone_in_string(self) -> None:
        """Test that scanner detects phone numbers."""
        scanner = RuntimeScanner(block=False)
        result = scanner.scan("Call me at 555-123-4567")

        assert result.has_violations
        assert any(v.violation_type == "phone" for v in result.violations)

    def test_detects_credit_card(self) -> None:
        """Test that scanner detects credit card numbers."""
        scanner = RuntimeScanner(block=False)
        # Valid Luhn checksum
        result = scanner.scan("Card number: 4111111111111111")

        assert result.has_violations
        assert any(v.violation_type == "credit_card" for v in result.violations)

    def test_detects_vin(self) -> None:
        """Test that scanner detects VINs."""
        scanner = RuntimeScanner(block=False)
        # Valid VIN with correct checksum
        result = scanner.scan("Vehicle: 5YJSA1DG9DFP14705")

        assert result.has_violations
        assert any(v.violation_type == "vin" for v in result.violations)

    def test_clean_string_no_violations(self) -> None:
        """Test that clean strings pass."""
        scanner = RuntimeScanner(block=False)
        result = scanner.scan("Hello, how can I help you today?")

        assert not result.has_violations
        assert len(result.violations) == 0

    def test_scans_dict_with_content_key(self) -> None:
        """Test scanning OpenAI-style message dicts."""
        scanner = RuntimeScanner(block=False)
        result = scanner.scan({"role": "user", "content": "My email is admin@company.com"})

        assert result.has_violations

    def test_scans_list_of_messages(self) -> None:
        """Test scanning list of messages."""
        scanner = RuntimeScanner(block=False)
        result = scanner.scan(
            [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "My SSN is 123-45-6789"},
            ]
        )

        assert result.has_violations

    def test_allowlist_filters_patterns(self) -> None:
        """Test that allowlist patterns are respected."""
        scanner = RuntimeScanner(block=False, allowlist=["example.com"])
        result = scanner.scan("Contact test@example.com for help")

        # example.com should be allowlisted
        email_violations = [v for v in result.violations if v.violation_type == "email"]
        assert len(email_violations) == 0

    def test_block_raises_exception(self) -> None:
        """Test that block=True raises PIIDetectedError."""
        scanner = RuntimeScanner(block=True)

        with pytest.raises(PIIDetectedError) as exc_info:
            scanner.check("My SSN is 123-45-6789")

        assert "ssn" in str(exc_info.value).lower()
        assert len(exc_info.value.violations) > 0

    def test_block_false_returns_violations(self) -> None:
        """Test that block=False returns violations without raising."""
        scanner = RuntimeScanner(block=False)
        violations = scanner.check("My SSN is 123-45-6789")

        assert len(violations) > 0


class TestScanPayload:
    """Tests for scan_payload function."""

    def test_blocks_pii_by_default(self) -> None:
        """Test that scan_payload blocks PII by default."""
        with pytest.raises(PIIDetectedError):
            scan_payload("Call me at 555-123-4567")

    def test_returns_violations_when_not_blocking(self) -> None:
        """Test scan_payload with block=False."""
        violations = scan_payload("My email is user@domain.org", block=False)

        assert len(violations) > 0

    def test_clean_payload_returns_empty(self) -> None:
        """Test that clean payloads return empty list."""
        violations = scan_payload("What's the weather like today?", block=False)

        assert len(violations) == 0


class TestScanLLMInputDecorator:
    """Tests for scan_llm_input decorator."""

    def test_decorator_blocks_pii_in_args(self) -> None:
        """Test that decorator scans positional arguments."""

        @scan_llm_input(block=True)
        def my_llm_call(prompt: str) -> str:
            return f"Response to: {prompt}"

        with pytest.raises(PIIDetectedError):
            my_llm_call("My SSN is 123-45-6789")

    def test_decorator_blocks_pii_in_kwargs(self) -> None:
        """Test that decorator scans keyword arguments."""

        @scan_llm_input(block=True)
        def my_llm_call(prompt: str) -> str:
            return f"Response to: {prompt}"

        with pytest.raises(PIIDetectedError):
            my_llm_call(prompt="Contact admin@company.com")

    def test_decorator_allows_clean_input(self) -> None:
        """Test that decorator allows clean input."""

        @scan_llm_input(block=True)
        def my_llm_call(prompt: str) -> str:
            return f"Response to: {prompt}"

        result = my_llm_call("What's the capital of France?")
        assert result == "Response to: What's the capital of France?"

    def test_decorator_with_allowlist(self) -> None:
        """Test decorator with allowlist."""

        @scan_llm_input(block=True, allowlist=["example.com"])
        def my_llm_call(prompt: str) -> str:
            return f"Response to: {prompt}"

        # Should not raise because example.com is allowlisted
        result = my_llm_call("Contact test@example.com")
        assert "example.com" in result

    def test_decorator_scans_specific_kwargs(self) -> None:
        """Test decorator with specific kwargs to scan."""

        @scan_llm_input(block=True, scan_kwargs=["user_input"])
        def my_llm_call(system: str, user_input: str) -> str:
            return f"{system}: {user_input}"

        # Should not raise because 'system' is not in scan_kwargs
        result = my_llm_call(
            system="admin@company.com",  # Not scanned
            user_input="Hello",  # Scanned but clean
        )
        assert "admin@company.com" in result


class TestPIIDetectedError:
    """Tests for PIIDetectedError exception."""

    def test_error_contains_violations(self) -> None:
        """Test that error contains violation list."""
        scanner = RuntimeScanner(block=True)

        try:
            scanner.check("SSN: 123-45-6789, Email: test@company.com")
        except PIIDetectedError as e:
            assert len(e.violations) >= 2
            violation_types = [v.violation_type for v in e.violations]
            assert "ssn" in violation_types
            assert "email" in violation_types

    def test_error_message_lists_types(self) -> None:
        """Test that error message mentions PII types."""
        scanner = RuntimeScanner(block=True)

        try:
            scanner.check("My email is admin@company.com")
        except PIIDetectedError as e:
            assert "email" in str(e).lower()
            assert "PII detected" in str(e)
