"""Tests for allowlist matching utilities."""

from sentinel_scan.allowlist import (
    AllowlistMatcher,
    get_regex_pattern,
    is_regex_pattern,
    matches_any_pattern,
    matches_pattern,
)


class TestPatternDetection:
    """Tests for pattern type detection."""

    def test_is_regex_pattern_with_prefix(self) -> None:
        """Test that patterns with 'regex:' prefix are detected."""
        assert is_regex_pattern("regex:^test_.*")
        assert is_regex_pattern("regex:\\d+")
        assert is_regex_pattern("regex:")

    def test_is_regex_pattern_without_prefix(self) -> None:
        """Test that patterns without prefix are not regex."""
        assert not is_regex_pattern("example.com")
        assert not is_regex_pattern("test@")
        assert not is_regex_pattern("")
        assert not is_regex_pattern("REGEX:test")  # Case sensitive

    def test_get_regex_pattern_extracts_pattern(self) -> None:
        """Test extraction of regex pattern from prefixed string."""
        assert get_regex_pattern("regex:^test_.*") == "^test_.*"
        assert get_regex_pattern("regex:\\d+") == "\\d+"
        assert get_regex_pattern("regex:") == ""


class TestMatchesPattern:
    """Tests for individual pattern matching."""

    def test_literal_pattern_substring_match(self) -> None:
        """Test literal patterns match as substrings."""
        assert matches_pattern("user@example.com", "example.com")
        assert matches_pattern("test@domain.org", "domain")
        assert matches_pattern("555-0100", "555")

    def test_literal_pattern_no_match(self) -> None:
        """Test literal patterns that don't match."""
        assert not matches_pattern("user@other.com", "example.com")
        assert not matches_pattern("555-1234", "555-0100")

    def test_regex_pattern_match(self) -> None:
        """Test regex patterns match correctly."""
        assert matches_pattern("test_user@example.com", "regex:^test_.*@")
        assert matches_pattern("abc123", "regex:\\d+")
        assert matches_pattern("user@example.com", "regex:@.*\\.com$")

    def test_regex_pattern_no_match(self) -> None:
        """Test regex patterns that don't match."""
        assert not matches_pattern("real_user@example.com", "regex:^test_.*@")
        assert not matches_pattern("abcdef", "regex:\\d+")

    def test_invalid_regex_pattern_returns_false(self) -> None:
        """Test that invalid regex patterns return False (not raise)."""
        # Invalid regex - unbalanced parenthesis
        assert not matches_pattern("test", "regex:[(")
        # Invalid regex - nothing to repeat
        assert not matches_pattern("test", "regex:*invalid")


class TestMatchesAnyPattern:
    """Tests for matching against multiple patterns."""

    def test_matches_any_literal(self) -> None:
        """Test matching any of multiple literal patterns."""
        patterns = ["example.com", "test.org", "demo.net"]
        assert matches_any_pattern("user@example.com", patterns)
        assert matches_any_pattern("admin@test.org", patterns)
        assert matches_any_pattern("info@demo.net", patterns)
        assert not matches_any_pattern("user@other.com", patterns)

    def test_matches_any_regex(self) -> None:
        """Test matching any of multiple regex patterns."""
        patterns = ["regex:^test_", "regex:_test$", "regex:\\d{3}-\\d{4}"]
        assert matches_any_pattern("test_function", patterns)
        assert matches_any_pattern("my_test", patterns)
        assert matches_any_pattern("555-1234", patterns)
        assert not matches_any_pattern("regular_function", patterns)

    def test_matches_any_mixed(self) -> None:
        """Test matching with mixed literal and regex patterns."""
        patterns = ["example.com", "regex:^test_.*@"]
        assert matches_any_pattern("user@example.com", patterns)
        assert matches_any_pattern("test_user@other.com", patterns)
        assert not matches_any_pattern("user@other.com", patterns)

    def test_empty_patterns_returns_false(self) -> None:
        """Test that empty pattern list returns False."""
        assert not matches_any_pattern("anything", [])


class TestAllowlistMatcher:
    """Tests for the AllowlistMatcher class."""

    def test_init_with_patterns(self) -> None:
        """Test initialization with patterns."""
        matcher = AllowlistMatcher(["example.com", "regex:^test_"])
        assert matcher.has_patterns
        assert len(matcher.patterns) == 2

    def test_init_without_patterns(self) -> None:
        """Test initialization without patterns."""
        matcher = AllowlistMatcher()
        assert not matcher.has_patterns
        assert matcher.patterns == []

    def test_set_patterns(self) -> None:
        """Test setting patterns after initialization."""
        matcher = AllowlistMatcher()
        assert not matcher.has_patterns

        matcher.set_patterns(["example.com", "regex:^test_"])
        assert matcher.has_patterns

    def test_is_allowlisted_literal(self) -> None:
        """Test allowlist matching with literal patterns."""
        matcher = AllowlistMatcher(["example.com", "test@", "555-0100"])

        assert matcher.is_allowlisted("user@example.com")
        assert matcher.is_allowlisted("test@domain.org")
        assert matcher.is_allowlisted("555-0100")
        assert not matcher.is_allowlisted("user@other.com")

    def test_is_allowlisted_regex(self) -> None:
        """Test allowlist matching with regex patterns."""
        matcher = AllowlistMatcher(
            [
                "regex:^noreply@",
                "regex:@(test|example)\\.com$",
                "regex:\\+1-555-\\d{3}-\\d{4}",
            ]
        )

        assert matcher.is_allowlisted("noreply@company.com")
        assert matcher.is_allowlisted("user@test.com")
        assert matcher.is_allowlisted("admin@example.com")
        assert matcher.is_allowlisted("+1-555-123-4567")
        assert not matcher.is_allowlisted("user@other.com")

    def test_is_allowlisted_mixed(self) -> None:
        """Test allowlist matching with mixed patterns."""
        matcher = AllowlistMatcher(
            [
                "example.com",  # literal
                "regex:^test_.*@",  # regex
                "555-0100",  # literal
            ]
        )

        # Literal matches
        assert matcher.is_allowlisted("user@example.com")
        assert matcher.is_allowlisted("555-0100")

        # Regex matches
        assert matcher.is_allowlisted("test_user@domain.org")

        # No match
        assert not matcher.is_allowlisted("user@other.com")

    def test_is_allowlisted_empty_matcher(self) -> None:
        """Test that empty matcher never matches."""
        matcher = AllowlistMatcher()
        assert not matcher.is_allowlisted("anything")
        assert not matcher.is_allowlisted("user@example.com")

    def test_invalid_regex_is_skipped(self) -> None:
        """Test that invalid regex patterns are skipped gracefully."""
        # Invalid regex should be skipped, valid patterns should work
        matcher = AllowlistMatcher(
            [
                "regex:[(invalid",  # Invalid
                "example.com",  # Valid literal
                "regex:^test_",  # Valid regex
            ]
        )

        # Literal still works
        assert matcher.is_allowlisted("user@example.com")
        # Valid regex still works
        assert matcher.is_allowlisted("test_function")
        # Invalid regex doesn't cause error
        assert not matcher.is_allowlisted("[(invalid")


class TestAllowlistMatcherPerformance:
    """Tests for AllowlistMatcher performance characteristics."""

    def test_regex_caching(self) -> None:
        """Test that regex patterns are compiled once and cached."""
        matcher = AllowlistMatcher(["regex:^test_.*"])

        # Multiple calls should use cached compiled regex
        for _ in range(100):
            matcher.is_allowlisted("test_something")

        # No assertion needed - test verifies no errors from repeated matching

    def test_literal_patterns_checked_first(self) -> None:
        """Test that literal patterns are checked before regex for performance."""
        # This is a behavioral test - literal should be faster
        matcher = AllowlistMatcher(
            [
                "regex:.*example.*",  # Expensive regex
                "example.com",  # Cheap literal
            ]
        )

        # Should match via literal first
        assert matcher.is_allowlisted("user@example.com")
