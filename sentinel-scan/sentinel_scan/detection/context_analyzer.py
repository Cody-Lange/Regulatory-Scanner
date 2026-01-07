"""Context analyzer for Sentinel Scan.

This module provides AST-based analysis to understand code context:
- Is this a test file?
- Is this inside a test function?
- Is this in a comment or docstring?
- Does this data flow to an LLM API call?
- Are there inline ignore comments?

This context is crucial for reducing false positives and
adjusting violation severity appropriately.
"""

import ast
import re
from pathlib import Path

from sentinel_scan.models import ScanContext

# Patterns for detecting test files
TEST_FILE_PATTERNS = [
    r"test_.*\.py$",
    r".*_test\.py$",
    r"tests?/.*\.py$",
    r".*_tests?\.py$",
]

# Patterns for detecting test functions
TEST_FUNCTION_PATTERNS = [
    r"^test_",
    r"_test$",
]

# Patterns for detecting LLM API calls
LLM_API_PATTERNS = [
    r"openai\.chat\.completions\.create",
    r"openai\.completions\.create",
    r"anthropic\.messages\.create",
    r"client\.chat\.completions\.create",
    r"langchain",
    r"llm\(",
    r"ChatOpenAI",
    r"Claude",
]

# Pattern for inline ignore comments
IGNORE_PATTERN = re.compile(
    r"#\s*sentinel-scan:\s*ignore(?:\s+(\w+(?:,\s*\w+)*))?",
    re.IGNORECASE,
)


class ContextAnalyzer:
    """Analyzes Python source code to understand context.

    The analyzer parses the AST once and provides methods to query
    context information for any location in the source.
    """

    def __init__(self, source: str, file_path: str) -> None:
        """Initialize the context analyzer.

        Args:
            source: Python source code as a string
            file_path: Path to the source file
        """
        self.source = source
        self.file_path = file_path
        self.lines = source.splitlines()
        self._tree: ast.AST | None = None
        self._function_ranges: list[tuple[str, int, int]] = []
        self._docstring_lines: set[int] = set()
        self._comment_lines: set[int] = set()
        self._llm_call_lines: set[int] = set()
        self._parse()

    def _parse(self) -> None:
        """Parse the source code and extract context information."""
        try:
            self._tree = ast.parse(self.source)
        except SyntaxError:
            # If parsing fails, we'll just have limited context
            self._tree = None
            return

        self._extract_function_ranges()
        self._extract_docstrings()
        self._extract_comments()
        self._extract_llm_calls()

    def _extract_function_ranges(self) -> None:
        """Extract line ranges for all functions."""
        if self._tree is None:
            return

        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_lineno = getattr(node, "end_lineno", node.lineno)
                self._function_ranges.append((node.name, node.lineno, end_lineno))

    def _extract_docstrings(self) -> None:
        """Extract line numbers that are part of docstrings."""
        if self._tree is None:
            return

        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    docstring_node = node.body[0]
                    start = docstring_node.lineno
                    end = getattr(docstring_node, "end_lineno", start)
                    for line in range(start, end + 1):
                        self._docstring_lines.add(line)

    def _extract_comments(self) -> None:
        """Extract line numbers that contain only comments."""
        for i, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                self._comment_lines.add(i)

    def _extract_llm_calls(self) -> None:
        """Extract line numbers that contain LLM API calls."""
        for i, line in enumerate(self.lines, start=1):
            for pattern in LLM_API_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    self._llm_call_lines.add(i)
                    break

    def is_test_file(self) -> bool:
        """Check if the current file is a test file.

        Returns:
            True if the file matches test file patterns
        """
        file_path_str = str(self.file_path)
        for pattern in TEST_FILE_PATTERNS:
            if re.search(pattern, file_path_str, re.IGNORECASE):
                return True
        return False

    def is_in_test_function(self, line_number: int) -> bool:
        """Check if a line is inside a test function.

        Args:
            line_number: 1-indexed line number

        Returns:
            True if the line is inside a test function
        """
        for func_name, start, end in self._function_ranges:
            if start <= line_number <= end:
                for pattern in TEST_FUNCTION_PATTERNS:
                    if re.search(pattern, func_name):
                        return True
        return False

    def is_in_comment(self, line_number: int) -> bool:
        """Check if a line is a comment-only line.

        Args:
            line_number: 1-indexed line number

        Returns:
            True if the line is a comment
        """
        return line_number in self._comment_lines

    def is_in_docstring(self, line_number: int) -> bool:
        """Check if a line is inside a docstring.

        Args:
            line_number: 1-indexed line number

        Returns:
            True if the line is in a docstring
        """
        return line_number in self._docstring_lines

    def has_inline_ignore(self, line_number: int) -> tuple[bool, set[str]]:
        """Check if a line has an inline ignore comment.

        Args:
            line_number: 1-indexed line number

        Returns:
            Tuple of (has_ignore, set of specific types to ignore)
        """
        if line_number < 1 or line_number > len(self.lines):
            return False, set()

        line = self.lines[line_number - 1]
        match = IGNORE_PATTERN.search(line)

        if not match:
            return False, set()

        # Check if specific types are mentioned
        types_str = match.group(1)
        if types_str:
            types = {t.strip().lower() for t in types_str.split(",")}
            return True, types

        # No specific types = ignore all
        return True, set()

    def flows_to_llm_api(self, line_number: int) -> bool:
        """Check if a line's data might flow to an LLM API call.

        This is a simplified check that looks for LLM API patterns
        on the same line or nearby lines.

        Args:
            line_number: 1-indexed line number

        Returns:
            True if the data might flow to an LLM API
        """
        # Check the line itself and a few lines around it
        for check_line in range(max(1, line_number - 5), min(len(self.lines) + 1, line_number + 5)):
            if check_line in self._llm_call_lines:
                return True
        return False

    def get_context(self, line_number: int) -> ScanContext:
        """Get full context information for a specific line.

        Args:
            line_number: 1-indexed line number

        Returns:
            ScanContext with all relevant context information
        """
        has_ignore, ignore_types = self.has_inline_ignore(line_number)

        return ScanContext(
            is_test_file=self.is_test_file(),
            is_in_test_function=self.is_in_test_function(line_number),
            is_in_comment=self.is_in_comment(line_number),
            is_in_docstring=self.is_in_docstring(line_number),
            flows_to_llm_api=self.flows_to_llm_api(line_number),
            has_inline_ignore=has_ignore,
            ignore_types=ignore_types,
        )
