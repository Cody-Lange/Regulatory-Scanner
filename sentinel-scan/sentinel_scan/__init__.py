"""Sentinel Scan - Runtime PII protection for LLM applications.

Prevent sensitive data from being sent to third-party LLM APIs.

Quick Start:
    >>> from sentinel_scan import protect_openai
    >>> protect_openai()  # Now all OpenAI calls are scanned for PII

    >>> # Or scan manually
    >>> from sentinel_scan import scan_payload
    >>> scan_payload("My SSN is 123-45-6789")
    PIIDetectedError: PII detected in LLM payload: ssn
"""

__version__ = "0.1.0"
__author__ = "Cody Lange"

from sentinel_scan.models import ScanResult, Severity, Violation
from sentinel_scan.runtime import (
    PIIDetectedError,
    RuntimeScanner,
    protect_anthropic,
    protect_langchain,
    protect_openai,
    scan_llm_input,
    scan_payload,
)

__all__ = [
    # Core models
    "ScanResult",
    "Severity",
    "Violation",
    # Runtime protection
    "PIIDetectedError",
    "RuntimeScanner",
    "protect_openai",
    "protect_anthropic",
    "protect_langchain",
    "scan_payload",
    "scan_llm_input",
    # Version
    "__version__",
]
