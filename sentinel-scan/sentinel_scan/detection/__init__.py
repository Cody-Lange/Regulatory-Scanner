"""Detection module for Sentinel Scan.

This module contains:
- Base detector interface
- Detector registry
- Built-in detectors (PII, VIN, custom)
- Context analyzer
"""

from sentinel_scan.detection.base import Detector
from sentinel_scan.detection.registry import DetectorRegistry

__all__ = ["Detector", "DetectorRegistry"]
