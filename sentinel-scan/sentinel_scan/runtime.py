"""Runtime LLM API protection for Sentinel Scan.

This module provides runtime interception of LLM API calls to detect
and block PII from being sent to third-party services.

Usage:
    # Option 1: Patch OpenAI client globally
    from sentinel_scan.runtime import protect_openai
    protect_openai()  # Now all OpenAI calls are scanned

    # Option 2: Use as a decorator
    from sentinel_scan.runtime import scan_llm_input

    @scan_llm_input(block=True)
    def my_llm_call(prompt: str) -> str:
        return openai.chat(prompt)

    # Option 3: Manual scanning
    from sentinel_scan.runtime import scan_payload

    violations = scan_payload(user_input)
    if violations:
        raise PIIDetectedError(violations)
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar

from sentinel_scan.detection.context_analyzer import ContextAnalyzer
from sentinel_scan.detection.pii_detector import PIIDetector
from sentinel_scan.detection.vin_detector import VINDetector

if TYPE_CHECKING:
    from sentinel_scan.models import Violation

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class PIIDetectedError(Exception):
    """Raised when PII is detected in LLM API payload."""

    def __init__(self, violations: list[Violation], message: str | None = None):
        self.violations = violations
        if message is None:
            types = ", ".join({v.violation_type for v in violations})
            message = (
                f"PII detected in LLM payload: {types}. Blocked to prevent compliance violation."
            )
        super().__init__(message)


@dataclass
class ScanResult:
    """Result of scanning a payload for PII."""

    has_violations: bool
    violations: list[Violation]
    payload_preview: str  # Truncated for logging

    def __bool__(self) -> bool:
        return self.has_violations


class RuntimeScanner:
    """Scans runtime data for PII before it's sent to LLM APIs."""

    def __init__(
        self,
        block: bool = True,
        log_violations: bool = True,
        allowlist: list[str] | None = None,
    ):
        """Initialize the runtime scanner.

        Args:
            block: If True, raise PIIDetectedError when PII is found.
                   If False, only log warnings.
            log_violations: Whether to log detected violations.
            allowlist: Patterns to allow (same format as config allowlist).
        """
        self.block = block
        self.log_violations = log_violations
        self.pii_detector = PIIDetector()
        self.vin_detector = VINDetector()

        if allowlist:
            self.pii_detector.set_allowlist(allowlist)
            self.vin_detector.set_allowlist(allowlist)

    def scan(self, payload: str | dict | list) -> ScanResult:
        """Scan a payload for PII.

        Args:
            payload: The data being sent to the LLM API.
                     Can be a string, dict, or list.

        Returns:
            ScanResult with any violations found.
        """
        # Convert payload to string for scanning
        text = self._payload_to_string(payload)

        if not text:
            return ScanResult(
                has_violations=False,
                violations=[],
                payload_preview="<empty>",
            )

        # Create minimal context (runtime data, not a file)
        context = ContextAnalyzer(text, "<runtime>")

        # Scan with all detectors
        violations: list[Violation] = []

        try:
            import ast

            tree = ast.parse("")  # Empty tree for runtime scanning
        except SyntaxError:
            tree = ast.Module(body=[], type_ignores=[])

        pii_violations = self.pii_detector.scan(text, tree, context, "<runtime>")
        vin_violations = self.vin_detector.scan(text, tree, context, "<runtime>")

        violations.extend(pii_violations)
        violations.extend(vin_violations)

        # Create preview (truncated for logging)
        preview = text[:100] + "..." if len(text) > 100 else text
        preview = preview.replace("\n", " ")

        return ScanResult(
            has_violations=len(violations) > 0,
            violations=violations,
            payload_preview=preview,
        )

    def check(self, payload: str | dict | list) -> list[Violation]:
        """Scan payload and optionally block if PII is found.

        Args:
            payload: The data being sent to the LLM API.

        Returns:
            List of violations found.

        Raises:
            PIIDetectedError: If block=True and PII is detected.
        """
        result = self.scan(payload)

        if result.has_violations:
            if self.log_violations:
                for v in result.violations:
                    logger.warning(
                        f"PII detected in LLM payload: {v.violation_type} "
                        f"({v.severity.name}) - {v.message}"
                    )

            if self.block:
                raise PIIDetectedError(result.violations)

        return result.violations

    def _payload_to_string(self, payload: str | dict | list) -> str:
        """Convert various payload types to a string for scanning."""
        if isinstance(payload, str):
            return payload
        elif isinstance(payload, dict):
            return self._dict_to_string(payload)
        elif isinstance(payload, list):
            return "\n".join(self._payload_to_string(item) for item in payload)
        else:
            return str(payload)

    def _dict_to_string(self, d: dict) -> str:
        """Extract text content from a dict (e.g., OpenAI message format)."""
        parts = []

        # Handle OpenAI-style messages
        if "content" in d:
            content = d["content"]
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                # Vision API format
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        parts.append(item["text"])

        # Handle other common keys
        for key in ["prompt", "text", "input", "query", "message"]:
            if key in d and isinstance(d[key], str):
                parts.append(d[key])

        # Recursively handle nested dicts
        for _key, value in d.items():
            if isinstance(value, dict):
                parts.append(self._dict_to_string(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        parts.append(self._dict_to_string(item))

        return "\n".join(parts)


# Global scanner instance
_default_scanner: RuntimeScanner | None = None


def get_scanner(
    block: bool = True,
    allowlist: list[str] | None = None,
) -> RuntimeScanner:
    """Get or create the default runtime scanner."""
    global _default_scanner
    if _default_scanner is None:
        _default_scanner = RuntimeScanner(block=block, allowlist=allowlist)
    return _default_scanner


def scan_payload(
    payload: str | dict | list,
    block: bool = True,
    allowlist: list[str] | None = None,
) -> list[Violation]:
    """Scan a payload for PII.

    This is the simplest way to check data before sending to an LLM.

    Args:
        payload: The data to scan (string, dict, or list).
        block: If True, raise PIIDetectedError when PII is found.
        allowlist: Patterns to allow.

    Returns:
        List of violations found.

    Raises:
        PIIDetectedError: If block=True and PII is detected.

    Example:
        >>> from sentinel_scan.runtime import scan_payload
        >>> scan_payload("Contact john@company.com for help")
        PIIDetectedError: PII detected in LLM payload: email
    """
    scanner = RuntimeScanner(block=block, allowlist=allowlist)
    return scanner.check(payload)


def scan_llm_input(
    block: bool = True,
    allowlist: list[str] | None = None,
    scan_args: list[int] | None = None,
    scan_kwargs: list[str] | None = None,
) -> Callable[[F], F]:
    """Decorator to scan function arguments for PII before LLM calls.

    Args:
        block: If True, raise PIIDetectedError when PII is found.
        allowlist: Patterns to allow.
        scan_args: Positional argument indices to scan (default: all).
        scan_kwargs: Keyword argument names to scan (default: common ones).

    Example:
        >>> @scan_llm_input(block=True)
        ... def ask_llm(prompt: str) -> str:
        ...     return openai.chat(prompt)
        ...
        >>> ask_llm("My SSN is 123-45-6789")
        PIIDetectedError: PII detected in LLM payload: ssn
    """
    default_kwargs = ["prompt", "messages", "content", "input", "query", "text"]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            scanner = RuntimeScanner(block=block, allowlist=allowlist)

            # Scan positional arguments
            args_to_scan = scan_args if scan_args is not None else range(len(args))
            for i in args_to_scan:
                if i < len(args):
                    scanner.check(args[i])

            # Scan keyword arguments
            kwargs_to_scan = scan_kwargs if scan_kwargs is not None else default_kwargs
            for key in kwargs_to_scan:
                if key in kwargs:
                    scanner.check(kwargs[key])

            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def protect_openai(
    block: bool = True,
    allowlist: list[str] | None = None,
) -> None:
    """Patch the OpenAI client to scan all requests for PII.

    This function monkey-patches the OpenAI library to intercept
    all API calls and scan message content for PII.

    Args:
        block: If True, raise PIIDetectedError when PII is found.
        allowlist: Patterns to allow.

    Example:
        >>> from sentinel_scan.runtime import protect_openai
        >>> protect_openai()
        >>>
        >>> # Now all OpenAI calls are protected
        >>> client = openai.OpenAI()
        >>> client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "My SSN is 123-45-6789"}]
        ... )
        PIIDetectedError: PII detected in LLM payload: ssn
    """
    try:
        import openai
    except ImportError as err:
        raise ImportError("OpenAI library not installed. Install with: pip install openai") from err

    scanner = RuntimeScanner(block=block, allowlist=allowlist)

    # Patch chat completions
    original_create = openai.resources.chat.completions.Completions.create

    @functools.wraps(original_create)
    def patched_create(self: Any, *args: Any, **kwargs: Any) -> Any:
        # Scan messages
        messages = kwargs.get("messages", [])
        for message in messages:
            if isinstance(message, dict):
                scanner.check(message)

        return original_create(self, *args, **kwargs)

    openai.resources.chat.completions.Completions.create = patched_create

    logger.info("OpenAI client protected with Sentinel Scan PII detection")


def protect_anthropic(
    block: bool = True,
    allowlist: list[str] | None = None,
) -> None:
    """Patch the Anthropic client to scan all requests for PII.

    Args:
        block: If True, raise PIIDetectedError when PII is found.
        allowlist: Patterns to allow.

    Example:
        >>> from sentinel_scan.runtime import protect_anthropic
        >>> protect_anthropic()
        >>>
        >>> client = anthropic.Anthropic()
        >>> client.messages.create(
        ...     messages=[{"role": "user", "content": "My email is john@company.com"}]
        ... )
        PIIDetectedError: PII detected in LLM payload: email
    """
    try:
        import anthropic
    except ImportError as err:
        raise ImportError(
            "Anthropic library not installed. Install with: pip install anthropic"
        ) from err

    scanner = RuntimeScanner(block=block, allowlist=allowlist)

    # Patch messages create
    original_create = anthropic.resources.messages.Messages.create

    @functools.wraps(original_create)
    def patched_create(self: Any, *args: Any, **kwargs: Any) -> Any:
        # Scan messages
        messages = kwargs.get("messages", [])
        for message in messages:
            if isinstance(message, dict):
                scanner.check(message)

        # Scan system prompt
        system = kwargs.get("system")
        if system:
            scanner.check(system)

        return original_create(self, *args, **kwargs)

    anthropic.resources.messages.Messages.create = patched_create

    logger.info("Anthropic client protected with Sentinel Scan PII detection")


def protect_langchain(
    block: bool = True,
    allowlist: list[str] | None = None,
) -> None:
    """Patch LangChain to scan all LLM inputs for PII.

    Args:
        block: If True, raise PIIDetectedError when PII is found.
        allowlist: Patterns to allow.
    """
    try:
        from langchain_core.language_models import base as lc_base
    except ImportError as err:
        raise ImportError(
            "LangChain not installed. Install with: pip install langchain-core"
        ) from err

    scanner = RuntimeScanner(block=block, allowlist=allowlist)

    # Patch the base invoke method
    original_invoke = lc_base.BaseLanguageModel.invoke

    @functools.wraps(original_invoke)
    def patched_invoke(self: Any, input: Any, *args: Any, **kwargs: Any) -> Any:
        scanner.check(input)
        return original_invoke(self, input, *args, **kwargs)

    lc_base.BaseLanguageModel.invoke = patched_invoke

    logger.info("LangChain protected with Sentinel Scan PII detection")
