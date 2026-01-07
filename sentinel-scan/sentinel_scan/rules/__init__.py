"""Rules module for Sentinel Scan.

This module contains:
- Rule engine for applying detection rules
- Allowlist management
- File/path exclusions
"""

from sentinel_scan.rules.engine import RuleEngine

__all__ = ["RuleEngine"]
