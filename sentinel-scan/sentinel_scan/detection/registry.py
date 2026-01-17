"""Detector registry for Sentinel Scan.

This module provides a central registry for detector classes,
allowing dynamic registration and instantiation of detectors.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentinel_scan.detection.base import Detector


class DetectorRegistry:
    """Central registry for detector classes.

    Provides methods to register, retrieve, and instantiate detectors.

    Example:
        @DetectorRegistry.register("pii")
        class PIIDetector(Detector):
            ...

        # Later, get all registered detectors
        detectors = DetectorRegistry.create_all(config)
    """

    _detectors: dict[str, type["Detector"]] = {}

    @classmethod
    def register(cls, name: str) -> Callable[[type["Detector"]], type["Detector"]]:
        """Decorator to register a detector class.

        Args:
            name: Unique identifier for the detector

        Returns:
            Decorator function that registers the class

        Example:
            @DetectorRegistry.register("pii")
            class PIIDetector(Detector):
                ...
        """

        def decorator(detector_cls: type["Detector"]) -> type["Detector"]:
            cls._detectors[name] = detector_cls
            return detector_cls

        return decorator

    @classmethod
    def get(cls, name: str) -> type["Detector"] | None:
        """Get a detector class by name.

        Args:
            name: The detector name to look up

        Returns:
            The detector class if found, None otherwise
        """
        return cls._detectors.get(name)

    @classmethod
    def all_names(cls) -> list[str]:
        """Get all registered detector names.

        Returns:
            List of registered detector names
        """
        return list(cls._detectors.keys())

    @classmethod
    def create_all(cls, config: dict) -> list["Detector"]:
        """Create instances of all enabled detectors.

        Args:
            config: Configuration dictionary

        Returns:
            List of instantiated detector objects
        """
        detectors = []
        for name, detector_cls in cls._detectors.items():
            # Check if detector is enabled in config
            detector_config = config.get("detectors", {}).get(name, {})
            if detector_config.get("enabled", True):
                detectors.append(detector_cls())
        return detectors

    @classmethod
    def clear(cls) -> None:
        """Clear all registered detectors. Useful for testing."""
        cls._detectors.clear()
