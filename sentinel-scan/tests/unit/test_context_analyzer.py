"""Unit tests for context analyzer."""


from sentinel_scan.detection.context_analyzer import ContextAnalyzer


class TestContextAnalyzer:
    """Tests for ContextAnalyzer."""

    def test_is_test_file_by_name(self):
        """Verify test file detection by name pattern."""
        analyzer = ContextAnalyzer("", "test_example.py")
        assert analyzer.is_test_file() is True

        analyzer = ContextAnalyzer("", "example_test.py")
        assert analyzer.is_test_file() is True

        analyzer = ContextAnalyzer("", "example.py")
        assert analyzer.is_test_file() is False

    def test_is_test_file_by_path(self):
        """Verify test file detection by path pattern."""
        analyzer = ContextAnalyzer("", "tests/test_example.py")
        assert analyzer.is_test_file() is True

        analyzer = ContextAnalyzer("", "src/tests/helpers.py")
        assert analyzer.is_test_file() is True

        analyzer = ContextAnalyzer("", "src/utils.py")
        assert analyzer.is_test_file() is False

    def test_is_in_test_function(self, context_analyzer_test: ContextAnalyzer):
        """Verify test function detection."""
        # Line inside test_email_validation function
        assert context_analyzer_test.is_in_test_function(8) is True

        # Line inside test_phone_validation function
        assert context_analyzer_test.is_in_test_function(14) is True

    def test_is_in_docstring(self, context_analyzer_pii: ContextAnalyzer):
        """Verify docstring detection."""
        # First line is the module docstring
        assert context_analyzer_pii.is_in_docstring(1) is True

        # Function docstring
        assert context_analyzer_pii.is_in_docstring(5) is True

    def test_is_in_comment(self):
        """Verify comment detection."""
        source = """x = 1
# This is a comment
y = 2
"""
        analyzer = ContextAnalyzer(source, "test.py")

        assert analyzer.is_in_comment(1) is False
        assert analyzer.is_in_comment(2) is True
        assert analyzer.is_in_comment(3) is False

    def test_inline_ignore_all(self):
        """Verify inline ignore comment parsing (ignore all)."""
        source = 'email = "test@test.com"  # sentinel-scan: ignore\n'
        analyzer = ContextAnalyzer(source, "test.py")

        has_ignore, types = analyzer.has_inline_ignore(1)
        assert has_ignore is True
        assert len(types) == 0  # Empty means ignore all

    def test_inline_ignore_specific(self):
        """Verify inline ignore comment parsing (specific types)."""
        source = 'data = "test"  # sentinel-scan: ignore email, phone\n'
        analyzer = ContextAnalyzer(source, "test.py")

        has_ignore, types = analyzer.has_inline_ignore(1)
        assert has_ignore is True
        assert "email" in types
        assert "phone" in types
        assert "ssn" not in types

    def test_inline_ignore_case_insensitive(self):
        """Verify inline ignore is case insensitive."""
        source = 'data = "test"  # SENTINEL-SCAN: IGNORE\n'
        analyzer = ContextAnalyzer(source, "test.py")

        has_ignore, _ = analyzer.has_inline_ignore(1)
        assert has_ignore is True

    def test_flows_to_llm_api(self, context_analyzer_pii: ContextAnalyzer):
        """Verify LLM API flow detection."""
        # Line near the openai.chat.completions.create call
        # The call is around line 13-16
        assert context_analyzer_pii.flows_to_llm_api(12) is True

    def test_get_context(self, context_analyzer_test: ContextAnalyzer):
        """Verify full context retrieval."""
        # Get context for a line in a test function
        ctx = context_analyzer_test.get_context(8)

        assert ctx.is_test_file is True
        assert ctx.is_in_test_function is True

    def test_handles_syntax_error(self):
        """Verify analyzer handles syntax errors gracefully."""
        source = "def broken(:\n    pass"
        analyzer = ContextAnalyzer(source, "broken.py")

        # Should not raise, just have limited functionality
        assert analyzer.is_test_file() is False
        ctx = analyzer.get_context(1)
        assert ctx is not None


class TestContextAnalyzerEdgeCases:
    """Edge case tests for ContextAnalyzer."""

    def test_empty_source(self):
        """Verify handling of empty source."""
        analyzer = ContextAnalyzer("", "empty.py")
        assert analyzer.is_test_file() is False
        assert analyzer.is_in_comment(1) is False

    def test_line_out_of_range(self):
        """Verify handling of out-of-range line numbers."""
        analyzer = ContextAnalyzer("x = 1\n", "test.py")

        has_ignore, types = analyzer.has_inline_ignore(999)
        assert has_ignore is False
        assert len(types) == 0

    def test_unicode_source(self):
        """Verify handling of unicode in source."""
        source = '# Comment with émoji 🎉\nx = "café"\n'
        analyzer = ContextAnalyzer(source, "unicode.py")

        assert analyzer.is_in_comment(1) is True
        assert analyzer.is_in_comment(2) is False
