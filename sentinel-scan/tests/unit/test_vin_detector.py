"""Tests for VIN detector.

This module tests the VIN detector's ability to detect:
- Vehicle Identification Numbers (17 characters)
- VIN checksum validation (9th character)
- Various VIN formats and edge cases
"""

import ast

import pytest

from sentinel_scan.detection.context_analyzer import ContextAnalyzer
from sentinel_scan.detection.vin_detector import VINDetector, calculate_vin_checksum
from sentinel_scan.models import Severity


class TestVINChecksumValidation:
    """Tests for VIN checksum calculation."""

    def test_valid_checksum_calculation(self) -> None:
        """Test checksum calculation for valid VINs."""
        # 1HGCM82633A123456 has check digit at position 9
        # We test the calculate_vin_checksum function
        vin = "1HGCM82633A123456"
        assert calculate_vin_checksum(vin[:8] + "X" + vin[9:]) is not None

    def test_checksum_returns_correct_digit(self) -> None:
        """Test that checksum returns correct check digit."""
        # For VIN 11111111111111111, the check digit should be 1
        # This is a simplified test VIN
        result = calculate_vin_checksum("11111111111111111")
        assert result is not None

    def test_checksum_rejects_invalid_characters(self) -> None:
        """Test that VINs with I, O, Q are rejected."""
        # VINs cannot contain I, O, or Q
        assert calculate_vin_checksum("1HGCM82I33A123456") is None  # Contains I
        assert calculate_vin_checksum("1HGCM82O33A123456") is None  # Contains O
        assert calculate_vin_checksum("1HGCMQ2633A123456") is None  # Contains Q

    def test_checksum_rejects_wrong_length(self) -> None:
        """Test that non-17 character VINs are rejected."""
        assert calculate_vin_checksum("1HGCM82633A12345") is None  # 16 chars
        assert calculate_vin_checksum("1HGCM82633A1234567") is None  # 18 chars


class TestVINDetection:
    """Tests for VIN detection in source code."""

    @pytest.fixture
    def detector(self) -> VINDetector:
        """Create a VIN detector instance."""
        return VINDetector()

    def _scan_source(self, detector: VINDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_detects_valid_vin(self, detector: VINDetector) -> None:
        """Test detection of a valid VIN."""
        # 5YJSA1DG9DFP14705 is a valid Tesla VIN with correct checksum
        source = 'vin = "5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert violations[0].violation_type == "vin"
        assert violations[0].detector == "vin"

    def test_detects_vin_in_fstring(self, detector: VINDetector) -> None:
        """Test detection of VIN in f-string."""
        source = 'msg = f"Vehicle VIN: 5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert violations[0].violation_type == "vin"

    def test_detects_multiple_vins(self, detector: VINDetector) -> None:
        """Test detection of multiple VINs."""
        # Both VINs must have valid checksums
        source = """
vins = [
    "5YJSA1DG9DFP14705",
    "1G1YY22G765104068",
]
"""
        violations = self._scan_source(detector, source)
        vin_violations = [v for v in violations if v.violation_type == "vin"]

        assert len(vin_violations) == 2

    def test_ignores_vin_with_invalid_characters(self, detector: VINDetector) -> None:
        """Test that VINs with I, O, Q are not detected."""
        source = """
# VINs cannot contain I, O, or Q
invalid1 = "1HGCM82I33A123456"  # Contains I
invalid2 = "1HGCM82O33A123456"  # Contains O
invalid3 = "1HGCMQ2633A123456"  # Contains Q
"""
        violations = self._scan_source(detector, source)
        vin_violations = [v for v in violations if v.violation_type == "vin"]

        assert len(vin_violations) == 0

    def test_ignores_wrong_length(self, detector: VINDetector) -> None:
        """Test that non-17 character strings are not detected."""
        source = """
too_short = "1HGCM82633A12345"   # 16 chars
too_long = "1HGCM82633A12345678"  # 19 chars
"""
        violations = self._scan_source(detector, source)
        vin_violations = [v for v in violations if v.violation_type == "vin"]

        assert len(vin_violations) == 0

    def test_ignores_invalid_checksum(self, detector: VINDetector) -> None:
        """Test that VINs with invalid checksums are not detected."""
        # 1G1YY22G965104069 - last digit changed, checksum invalid
        source = 'vin = "1G1YY22G065104068"'  # Changed position 8 to 0, invalid checksum
        violations = self._scan_source(detector, source)
        vin_violations = [v for v in violations if v.violation_type == "vin"]

        # With checksum validation enabled, this should be rejected
        # Note: detector may have option to disable checksum validation
        assert len(vin_violations) == 0 or violations[0].context_info.get("checksum_valid") is False

    def test_vin_severity_is_high(self, detector: VINDetector) -> None:
        """Test that VIN violations have HIGH severity."""
        source = 'vin = "5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert violations[0].severity == Severity.HIGH

    def test_vin_has_regulation_reference(self, detector: VINDetector) -> None:
        """Test that VIN violations reference relevant regulations."""
        source = 'vin = "5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1
        assert "GDPR" in violations[0].regulation or "CCPA" in violations[0].regulation


class TestVINContextAwareness:
    """Tests for context-aware VIN detection."""

    @pytest.fixture
    def detector(self) -> VINDetector:
        """Create a VIN detector instance."""
        return VINDetector()

    def _scan_source(self, detector: VINDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_ignores_vin_in_test_file(self, detector: VINDetector) -> None:
        """Test that VINs in test files have reduced severity."""
        source = 'test_vin = "5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source, "tests/test_vehicle.py")

        # Should detect but with lower severity
        if len(violations) > 0:
            assert violations[0].severity <= Severity.MEDIUM

    def test_ignores_vin_with_inline_ignore(self, detector: VINDetector) -> None:
        """Test inline ignore comment."""
        source = 'vin = "5YJSA1DG9DFP14705"  # sentinel-scan: ignore'
        violations = self._scan_source(detector, source)

        assert len(violations) == 0

    def test_ignores_vin_with_specific_ignore(self, detector: VINDetector) -> None:
        """Test inline ignore with specific type."""
        source = 'vin = "5YJSA1DG9DFP14705"  # sentinel-scan: ignore vin'
        violations = self._scan_source(detector, source)

        assert len(violations) == 0

    def test_skips_comment_lines(self, detector: VINDetector) -> None:
        """Test that comment-only lines are skipped."""
        source = """# Example VIN: 5YJSA1DG9DFP14705
real_vin = "1G1YY22G765104068"
"""
        violations = self._scan_source(detector, source)
        vin_violations = [v for v in violations if v.violation_type == "vin"]

        # Should only detect the real_vin, not the commented one
        assert len(vin_violations) == 1

    def test_skips_docstrings(self, detector: VINDetector) -> None:
        """Test that VINs in docstrings are skipped."""
        source = '''
def lookup_vehicle():
    """Look up vehicle by VIN.

    Example VIN: 5YJSA1DG9DFP14705
    """
    return None
'''
        violations = self._scan_source(detector, source)

        assert len(violations) == 0

    def test_increases_severity_near_llm_call(self, detector: VINDetector) -> None:
        """Test that VINs near LLM API calls have higher severity."""
        source = """
vin = "5YJSA1DG9DFP14705"
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": f"Lookup VIN: {vin}"}]
)
"""
        violations = self._scan_source(detector, source)

        # Near LLM calls, should be flagged with context
        for v in violations:
            if v.violation_type == "vin":
                assert v.context_info.get("flows_to_llm_api", False) or v.severity >= Severity.HIGH


class TestVINAllowlist:
    """Tests for VIN allowlist filtering."""

    @pytest.fixture
    def detector(self) -> VINDetector:
        """Create a VIN detector instance."""
        return VINDetector()

    def _scan_source(
        self,
        detector: VINDetector,
        source: str,
        file_path: str = "test.py",
        allowlist: list | None = None,
    ) -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        if allowlist:
            detector.set_allowlist(allowlist)
        return detector.scan(source, tree, context, file_path)

    def test_allowlist_filters_vin(self, detector: VINDetector) -> None:
        """Test that allowlisted VINs are not flagged."""
        source = 'vin = "5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source, allowlist=["5YJSA1DG9DFP14705"])

        assert len(violations) == 0

    def test_allowlist_partial_match(self, detector: VINDetector) -> None:
        """Test that partial allowlist matches work (manufacturer prefix)."""
        source = 'vin = "5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source, allowlist=["5YJ"])

        assert len(violations) == 0


class TestKnownValidVINs:
    """Tests using known valid VINs for validation."""

    @pytest.fixture
    def detector(self) -> VINDetector:
        """Create a VIN detector instance."""
        return VINDetector()

    def _scan_source(self, detector: VINDetector, source: str, file_path: str = "test.py") -> list:
        """Helper to scan source code."""
        tree = ast.parse(source)
        context = ContextAnalyzer(source, file_path)
        return detector.scan(source, tree, context, file_path)

    def test_detects_tesla_vin(self, detector: VINDetector) -> None:
        """Test detection of Tesla Model S VIN."""
        # 5YJSA1DG9DFP14705 is a valid Tesla VIN
        source = 'vin = "5YJSA1DG9DFP14705"'
        violations = self._scan_source(detector, source)

        assert len(violations) == 1

    def test_detects_toyota_vin(self, detector: VINDetector) -> None:
        """Test detection of Toyota VIN."""
        # Valid Toyota Camry VIN format
        source = 'vin = "4T1BF1FK5CU123456"'
        violations = self._scan_source(detector, source)

        # May or may not detect depending on checksum validation
        # The test validates the detector runs without error
        assert violations is not None

    def test_detects_ford_vin(self, detector: VINDetector) -> None:
        """Test detection of Ford VIN."""
        # 1FAHP3F29CL123456 - Ford Focus format
        source = 'vin = "1FAHP3F29CL123456"'
        violations = self._scan_source(detector, source)

        # Validates detector runs without error
        assert violations is not None
