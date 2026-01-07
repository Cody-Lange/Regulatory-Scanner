"""Output formatters for Sentinel Scan.

This module contains formatters for different output formats:
- Console (Rich-formatted terminal output)
- JSON (machine-readable for CI/CD)
- VS Code (diagnostics format)
"""

from sentinel_scan.formatters.console import ConsoleFormatter
from sentinel_scan.formatters.json_output import JSONFormatter

__all__ = ["ConsoleFormatter", "JSONFormatter"]
