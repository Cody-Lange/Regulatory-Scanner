"""JSON formatter for Sentinel Scan.

This module provides JSON output for scan results,
suitable for CI/CD integration and audit logging.
"""

import json
from typing import Any

from sentinel_scan.models import ScanResult


class JSONFormatter:
    """Formats scan results as JSON."""

    def __init__(self, indent: int = 2, sort_keys: bool = False) -> None:
        """Initialize the JSON formatter.

        Args:
            indent: Number of spaces for indentation
            sort_keys: Whether to sort dictionary keys
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def format(self, result: ScanResult) -> str:
        """Format scan results as JSON string.

        Args:
            result: Scan results to format

        Returns:
            JSON string representation
        """
        return json.dumps(
            result.to_dict(),
            indent=self.indent,
            sort_keys=self.sort_keys,
            default=self._json_serializer,
        )

    def format_dict(self, result: ScanResult) -> dict[str, Any]:
        """Format scan results as dictionary.

        Args:
            result: Scan results to format

        Returns:
            Dictionary representation
        """
        return result.to_dict()

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for non-standard types.

        Args:
            obj: Object to serialize

        Returns:
            JSON-serializable representation
        """
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)
