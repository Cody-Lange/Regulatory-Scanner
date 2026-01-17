"""Base detector interface for Sentinel Scan.

This module defines the abstract base class that all detectors must implement.
"""

import ast
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sentinel_scan.models import Violation

if TYPE_CHECKING:
    from sentinel_scan.detection.context_analyzer import ContextAnalyzer


class Detector(ABC):
    """Abstract base class for compliance violation detectors.

    All detectors must implement:
    - name: Unique identifier for the detector
    - scan: Method to detect violations in source code

    Example:
        class EmailDetector(Detector):
            @property
            def name(self) -> str:
                return "email"

            def scan(self, source, tree, context, file_path) -> list[Violation]:
                # Detection logic here
                return violations
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying this detector.

        Returns:
            String identifier like "pii", "vin", "custom"
        """
        ...

    @abstractmethod
    def scan(
        self,
        source: str,
        tree: ast.AST,
        context: "ContextAnalyzer",
        file_path: str,
    ) -> list[Violation]:
        """Scan source code for compliance violations.

        Args:
            source: The source code as a string
            tree: Parsed AST of the source code
            context: Context analyzer for determining code context
            file_path: Path to the file being scanned

        Returns:
            List of Violation objects found in the source
        """
        ...

    def is_enabled(self, config: dict) -> bool:
        """Check if this detector is enabled in the configuration.

        Args:
            config: Detector configuration dictionary

        Returns:
            True if enabled, False otherwise
        """
        detector_config = config.get("detectors", {}).get(self.name, {})
        return bool(detector_config.get("enabled", True))
