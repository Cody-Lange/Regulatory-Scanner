"""Tests for the RuleEngine.

This module tests the rule engine's ability to:
- Filter violations through allowlists
- Handle regex and literal patterns
- Adjust severity based on context
- Exclude files by path patterns
"""

from sentinel_scan.models import Severity, Violation
from sentinel_scan.rules.engine import RuleEngine


class TestRuleEngineInitialization:
    """Tests for RuleEngine initialization."""

    def test_initializes_with_empty_config(self) -> None:
        """Test that engine initializes with empty config."""
        engine = RuleEngine({})

        assert engine.global_allowlist == []
        assert engine.exclusion_paths == []

    def test_initializes_with_allowlist(self) -> None:
        """Test that engine loads allowlist from config."""
        config = {"allowlist": ["example.com", "test@"]}
        engine = RuleEngine(config)

        assert len(engine.global_allowlist) == 2

    def test_initializes_with_exclusions(self) -> None:
        """Test that engine loads exclusion paths."""
        config = {"exclusions": {"paths": ["*/tests/*", "*/.venv/*"]}}
        engine = RuleEngine(config)

        assert len(engine.exclusion_paths) == 2


class TestFileExclusion:
    """Tests for file exclusion logic."""

    def test_excludes_matching_path(self) -> None:
        """Test that matching paths are excluded."""
        config = {"exclusions": {"paths": ["*/tests/*"]}}
        engine = RuleEngine(config)

        assert engine.should_exclude_file("/project/tests/test_foo.py")

    def test_does_not_exclude_non_matching_path(self) -> None:
        """Test that non-matching paths are not excluded."""
        config = {"exclusions": {"paths": ["*/tests/*"]}}
        engine = RuleEngine(config)

        assert not engine.should_exclude_file("/project/src/main.py")

    def test_excludes_venv_path(self) -> None:
        """Test that venv paths are excluded."""
        config = {"exclusions": {"paths": ["*/.venv/*"]}}
        engine = RuleEngine(config)

        assert engine.should_exclude_file("/project/.venv/lib/python3.11/site.py")


class TestAllowlistFiltering:
    """Tests for allowlist filtering."""

    def create_violation(
        self, matched_text: str, detector: str = "pii", violation_type: str = "email"
    ) -> Violation:
        """Create a test violation."""
        return Violation(
            file_path="test.py",
            line_number=1,
            column_number=1,
            end_column=len(matched_text) + 1,
            detector=detector,
            violation_type=violation_type,
            matched_text=matched_text,
            severity=Severity.HIGH,
            regulation="GDPR",
            message="Test violation",
            recommendation="Fix it",
        )

    def test_literal_allowlist_match(self) -> None:
        """Test that literal patterns are matched as substrings."""
        config = {"allowlist": ["example.com"]}
        engine = RuleEngine(config)

        assert engine.is_allowlisted("user@example.com", "pii")

    def test_literal_allowlist_no_match(self) -> None:
        """Test that non-matching text is not allowlisted."""
        config = {"allowlist": ["example.com"]}
        engine = RuleEngine(config)

        assert not engine.is_allowlisted("user@test.org", "pii")

    def test_regex_allowlist_match(self) -> None:
        """Test that regex patterns are matched."""
        config = {"allowlist": ["regex:^test_.*@"]}
        engine = RuleEngine(config)

        assert engine.is_allowlisted("test_bot@company.com", "pii")

    def test_regex_allowlist_no_match(self) -> None:
        """Test that non-matching text is not allowlisted by regex."""
        config = {"allowlist": ["regex:^test_.*@"]}
        engine = RuleEngine(config)

        assert not engine.is_allowlisted("user@company.com", "pii")

    def test_detector_specific_allowlist(self) -> None:
        """Test that detector-specific allowlists work."""
        config = {
            "allowlist": [],
            "detectors": {"pii": {"allowlist": ["internal.example.com"]}},
        }
        engine = RuleEngine(config)

        assert engine.is_allowlisted("admin@internal.example.com", "pii")
        assert not engine.is_allowlisted("admin@internal.example.com", "vin")

    def test_filter_violations_removes_allowlisted(self) -> None:
        """Test that filter_violations removes allowlisted violations."""
        config = {"allowlist": ["example.com"]}
        engine = RuleEngine(config)

        violations = [
            self.create_violation("user@example.com"),
            self.create_violation("admin@company.org"),
        ]

        filtered = engine.filter_violations(violations)

        assert len(filtered) == 1
        assert filtered[0].matched_text == "admin@company.org"


class TestSeverityAdjustment:
    """Tests for severity adjustment."""

    def create_violation(self, severity: Severity = Severity.HIGH) -> Violation:
        """Create a test violation with given severity."""
        return Violation(
            file_path="test.py",
            line_number=1,
            column_number=1,
            end_column=10,
            detector="pii",
            violation_type="email",
            matched_text="test@example.com",
            severity=severity,
            regulation="GDPR",
            message="Test",
            recommendation="Fix",
        )

    def test_lowers_severity_for_test_code(self) -> None:
        """Test that severity is lowered for test code."""
        engine = RuleEngine({})
        violation = self.create_violation(Severity.HIGH)

        adjusted = engine.adjust_severity(violation, is_test=True, flows_to_llm=False)

        assert adjusted == Severity.LOW

    def test_elevates_severity_for_llm_flow(self) -> None:
        """Test that severity is elevated when data flows to LLM."""
        engine = RuleEngine({})
        violation = self.create_violation(Severity.HIGH)

        adjusted = engine.adjust_severity(violation, is_test=False, flows_to_llm=True)

        assert adjusted == Severity.CRITICAL

    def test_keeps_severity_for_normal_code(self) -> None:
        """Test that severity is unchanged for normal code."""
        engine = RuleEngine({})
        violation = self.create_violation(Severity.HIGH)

        adjusted = engine.adjust_severity(violation, is_test=False, flows_to_llm=False)

        assert adjusted == Severity.HIGH


class TestSeverityFiltering:
    """Tests for severity filtering."""

    def create_violations(self) -> list[Violation]:
        """Create test violations with different severities."""
        severities = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        violations = []
        for i, sev in enumerate(severities):
            violations.append(
                Violation(
                    file_path="test.py",
                    line_number=i + 1,
                    column_number=1,
                    end_column=10,
                    detector="pii",
                    violation_type="email",
                    matched_text=f"test{i}@example.com",
                    severity=sev,
                    regulation="GDPR",
                    message="Test",
                    recommendation="Fix",
                )
            )
        return violations

    def test_filters_by_minimum_severity(self) -> None:
        """Test filtering violations by minimum severity."""
        engine = RuleEngine({})
        violations = self.create_violations()

        # Filter to HIGH and above
        filtered = engine.filter_by_severity(violations, Severity.HIGH)

        assert len(filtered) == 2
        assert all(v.severity >= Severity.HIGH for v in filtered)

    def test_filter_all_when_critical_only(self) -> None:
        """Test filtering to critical only."""
        engine = RuleEngine({})
        violations = self.create_violations()

        filtered = engine.filter_by_severity(violations, Severity.CRITICAL)

        assert len(filtered) == 1
        assert filtered[0].severity == Severity.CRITICAL

    def test_filter_none_when_low(self) -> None:
        """Test that LOW filter includes all violations."""
        engine = RuleEngine({})
        violations = self.create_violations()

        filtered = engine.filter_by_severity(violations, Severity.LOW)

        assert len(filtered) == 4
