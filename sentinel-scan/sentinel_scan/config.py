"""Configuration management for Sentinel Scan.

This module handles:
- Loading YAML configuration files
- Validating configuration
- Merging hierarchical configs (global -> project -> file)
- Providing default configuration
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DetectorConfig:
    """Configuration for a single detector."""

    enabled: bool = True
    severity: str = "high"
    allowlist: list[str] = field(default_factory=list)


@dataclass
class Settings:
    """Global scanner settings."""

    min_severity: str = "low"
    exit_on_violation: bool = True


@dataclass
class Exclusions:
    """File and path exclusions."""

    paths: list[str] = field(default_factory=list)


@dataclass
class Config:
    """Main configuration for Sentinel Scan.

    Attributes:
        version: Configuration schema version
        settings: Global scanner settings
        allowlist: Global allowlist patterns
        exclusions: File/path exclusions
        detectors: Per-detector configuration
    """

    version: str = "1.0"
    settings: Settings = field(default_factory=Settings)
    allowlist: list[str] = field(default_factory=list)
    exclusions: Exclusions = field(default_factory=Exclusions)
    detectors: dict[str, Any] = field(default_factory=dict)


def get_default_config() -> Config:
    """Get the default configuration.

    Returns:
        Config with sensible defaults
    """
    return Config(
        version="1.0",
        settings=Settings(min_severity="low", exit_on_violation=True),
        allowlist=["example.com", "test@", "555-0100"],
        exclusions=Exclusions(paths=["*/tests/*", "*/.venv/*", "*/__pycache__/*"]),
        detectors={
            "pii": {
                "enabled": True,
                "patterns": {
                    "email": {"enabled": True, "severity": "high"},
                    "phone": {"enabled": True, "severity": "high"},
                    "ssn": {"enabled": True, "severity": "critical"},
                    "credit_card": {"enabled": True, "severity": "critical"},
                },
            },
            "vin": {"enabled": True, "validate_checksum": True},
        },
    )


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the config file. If None, uses defaults.

    Returns:
        Config object with loaded or default settings

    Raises:
        FileNotFoundError: If config_path is specified but doesn't exist
        yaml.YAMLError: If the config file is invalid YAML
    """
    if config_path is None:
        return get_default_config()

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open() as f:
        data = yaml.safe_load(f)

    # TODO: Implement full config parsing and validation in Phase 1
    return get_default_config()


def find_config_file(start_path: Path | None = None) -> Path | None:
    """Find a config file by walking up the directory tree.

    Args:
        start_path: Directory to start searching from. Defaults to cwd.

    Returns:
        Path to config file if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()
    config_names = ["sentinel_scan.yaml", "sentinel_scan.yml", ".sentinel_scan.yaml"]

    while current != current.parent:
        for name in config_names:
            config_path = current / name
            if config_path.exists():
                return config_path
        current = current.parent

    return None
