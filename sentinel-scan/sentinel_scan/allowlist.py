"""Allowlist matching utilities for Sentinel Scan.

This module provides utilities for matching text against allowlist patterns,
supporting both literal substring matches and regex patterns.

Pattern types:
- Literal: Any pattern not starting with 'regex:' - matches if pattern is substring of text
- Regex: Patterns starting with 'regex:' - matches if regex pattern matches text

Examples:
    - "example.com" - literal, matches "user@example.com", "test.example.com"
    - "regex:^test_.*@" - regex, matches "test_user@domain.com"
    - "regex:\\d{3}-\\d{4}" - regex, matches "555-1234"
"""

import logging
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

# Prefix for regex patterns
REGEX_PREFIX = "regex:"


@lru_cache(maxsize=256)
def _compile_regex(pattern: str) -> re.Pattern[str] | None:
    """Compile a regex pattern with caching.

    Args:
        pattern: Regex pattern string (without 'regex:' prefix)

    Returns:
        Compiled regex pattern, or None if invalid
    """
    try:
        return re.compile(pattern)
    except re.error as e:
        logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        return None


def is_regex_pattern(pattern: str) -> bool:
    """Check if a pattern is a regex pattern.

    Args:
        pattern: The allowlist pattern

    Returns:
        True if pattern starts with 'regex:' prefix
    """
    return pattern.startswith(REGEX_PREFIX)


def get_regex_pattern(pattern: str) -> str:
    """Extract the regex pattern from a prefixed pattern.

    Args:
        pattern: The allowlist pattern with 'regex:' prefix

    Returns:
        The regex pattern without the prefix
    """
    return pattern[len(REGEX_PREFIX) :]


def matches_pattern(text: str, pattern: str) -> bool:
    """Check if text matches an allowlist pattern.

    Args:
        text: The text to check
        pattern: The allowlist pattern (literal or regex)

    Returns:
        True if the text matches the pattern
    """
    if is_regex_pattern(pattern):
        regex_str = get_regex_pattern(pattern)
        compiled = _compile_regex(regex_str)
        if compiled is None:
            return False
        return compiled.search(text) is not None
    else:
        # Literal substring match
        return pattern in text


def matches_any_pattern(text: str, patterns: list[str]) -> bool:
    """Check if text matches any allowlist pattern.

    Args:
        text: The text to check
        patterns: List of allowlist patterns (literal or regex)

    Returns:
        True if the text matches any pattern
    """
    return any(matches_pattern(text, pattern) for pattern in patterns)


class AllowlistMatcher:
    """Allowlist matcher with support for literal and regex patterns.

    This class provides efficient matching against a list of patterns,
    separating regex and literal patterns for optimized matching.
    """

    def __init__(self, patterns: list[str] | None = None) -> None:
        """Initialize the allowlist matcher.

        Args:
            patterns: List of allowlist patterns
        """
        self._patterns: list[str] = []
        self._literal_patterns: list[str] = []
        self._regex_patterns: list[tuple[str, re.Pattern[str]]] = []

        if patterns:
            self.set_patterns(patterns)

    def set_patterns(self, patterns: list[str]) -> None:
        """Set allowlist patterns.

        Args:
            patterns: List of allowlist patterns (literal or regex)
        """
        self._patterns = patterns
        self._literal_patterns = []
        self._regex_patterns = []

        for pattern in patterns:
            if is_regex_pattern(pattern):
                regex_str = get_regex_pattern(pattern)
                compiled = _compile_regex(regex_str)
                if compiled is not None:
                    self._regex_patterns.append((pattern, compiled))
            else:
                self._literal_patterns.append(pattern)

    def is_allowlisted(self, text: str) -> bool:
        """Check if text is allowlisted.

        Args:
            text: The text to check

        Returns:
            True if the text matches any allowlist pattern
        """
        # Check literal patterns first (faster)
        if any(pattern in text for pattern in self._literal_patterns):
            return True

        # Check regex patterns
        return any(compiled.search(text) is not None for _, compiled in self._regex_patterns)

    @property
    def patterns(self) -> list[str]:
        """Get the current patterns."""
        return self._patterns

    @property
    def has_patterns(self) -> bool:
        """Check if any patterns are configured."""
        return bool(self._literal_patterns or self._regex_patterns)
