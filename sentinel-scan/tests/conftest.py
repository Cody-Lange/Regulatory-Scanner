"""Pytest configuration and shared fixtures for Sentinel Scan tests."""

import pytest

from sentinel_scan.config import Config, Exclusions, Settings, get_default_config
from sentinel_scan.detection.context_analyzer import ContextAnalyzer
from sentinel_scan.models import ScanResult, Severity, Violation


@pytest.fixture
def default_config() -> Config:
    """Provide default configuration for tests."""
    return get_default_config()


@pytest.fixture
def strict_config() -> Config:
    """Provide strict configuration (no allowlist) for tests."""
    return Config(
        version="1.0",
        settings=Settings(min_severity="low", exit_on_violation=True),
        allowlist=[],
        exclusions=Exclusions(paths=[]),
        detectors={
            "pii": {"enabled": True},
            "vin": {"enabled": True, "validate_checksum": True},
        },
    )


@pytest.fixture
def sample_violation() -> Violation:
    """Provide a sample violation for tests."""
    return Violation(
        file_path="src/example.py",
        line_number=10,
        column_number=8,
        end_column=28,
        detector="pii",
        violation_type="email",
        matched_text="user@exam...e.com",
        severity=Severity.HIGH,
        regulation="GDPR Article 6",
        message="Email address detected",
        recommendation="Hash or remove before sending to LLM",
        context_info={"is_test": False},
    )


@pytest.fixture
def sample_scan_result(sample_violation: Violation) -> ScanResult:
    """Provide a sample scan result for tests."""
    return ScanResult(
        files_scanned=5,
        lines_scanned=500,
        violations=[sample_violation],
        scan_duration_ms=150,
    )


@pytest.fixture
def empty_scan_result() -> ScanResult:
    """Provide an empty scan result (no violations)."""
    return ScanResult(
        files_scanned=3,
        lines_scanned=300,
        violations=[],
        scan_duration_ms=100,
    )


@pytest.fixture
def clean_python_source() -> str:
    """Provide Python source code with no violations."""
    return '''"""Module for processing data."""


def process_data(data: list) -> list:
    """Process the input data.

    Args:
        data: List of items to process

    Returns:
        Processed list of items
    """
    result = []
    for item in data:
        result.append(item.upper())
    return result


class DataProcessor:
    """A class for processing data."""

    def __init__(self, name: str) -> None:
        self.name = name

    def run(self) -> None:
        print(f"Running {self.name}")
'''


@pytest.fixture
def pii_python_source() -> str:
    """Provide Python source code with PII violations."""
    return '''"""Module with PII violations."""


def send_to_llm(data: str) -> str:
    """Send data to LLM API."""
    email = "john.doe@company.com"
    phone = "555-123-4567"
    ssn = "123-45-6789"

    # Build the prompt
    prompt = f"Process this data: {email}, {phone}"

    # Send to OpenAI
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response
'''


@pytest.fixture
def vin_python_source() -> str:
    """Provide Python source code with VIN violations."""
    return '''"""Module with VIN data."""


def lookup_vehicle(vin: str) -> dict:
    """Look up vehicle information."""
    # Example VIN
    test_vin = "1HGCM82633A123456"

    # Send to analytics
    return {"vin": vin, "status": "found"}
'''


@pytest.fixture
def test_file_source() -> str:
    """Provide Python test file source code."""
    return '''"""Test module."""

import pytest


def test_email_validation():
    """Test email validation."""
    test_email = "test@example.com"
    assert validate_email(test_email)


def test_phone_validation():
    """Test phone validation."""
    test_phone = "555-123-4567"
    assert validate_phone(test_phone)


class TestDataProcessor:
    """Tests for DataProcessor."""

    def test_process(self):
        ssn = "123-45-6789"  # Test SSN
        assert process(ssn) is not None
'''


@pytest.fixture
def context_analyzer_clean(clean_python_source: str) -> ContextAnalyzer:
    """Provide context analyzer for clean source."""
    return ContextAnalyzer(clean_python_source, "src/clean.py")


@pytest.fixture
def context_analyzer_pii(pii_python_source: str) -> ContextAnalyzer:
    """Provide context analyzer for PII source."""
    return ContextAnalyzer(pii_python_source, "src/pii_example.py")


@pytest.fixture
def context_analyzer_test(test_file_source: str) -> ContextAnalyzer:
    """Provide context analyzer for test file."""
    return ContextAnalyzer(test_file_source, "tests/test_validation.py")
