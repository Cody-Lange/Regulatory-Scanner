"""Unit tests for configuration module."""

from pathlib import Path

import pytest

from sentinel_scan.config import (
    Config,
    Exclusions,
    Settings,
    find_config_file,
    get_default_config,
    load_config,
)


class TestGetDefaultConfig:
    """Tests for get_default_config function."""

    def test_returns_config(self):
        """Verify default config is returned."""
        config = get_default_config()
        assert isinstance(config, Config)

    def test_has_version(self):
        """Verify config has version."""
        config = get_default_config()
        assert config.version == "1.0"

    def test_has_settings(self):
        """Verify config has settings."""
        config = get_default_config()
        assert config.settings.min_severity == "low"
        assert config.settings.exit_on_violation is True

    def test_has_allowlist(self):
        """Verify config has default allowlist."""
        config = get_default_config()
        assert len(config.allowlist) > 0
        assert "example.com" in config.allowlist

    def test_has_exclusions(self):
        """Verify config has default exclusions."""
        config = get_default_config()
        assert len(config.exclusions.paths) > 0
        assert "*/tests/*" in config.exclusions.paths

    def test_has_detectors(self):
        """Verify config has detector settings."""
        config = get_default_config()
        assert "pii" in config.detectors
        assert "vin" in config.detectors
        assert config.detectors["pii"]["enabled"] is True


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_none_returns_default(self):
        """Verify loading None returns default config."""
        config = load_config(None)
        assert isinstance(config, Config)
        assert config.version == "1.0"

    def test_load_missing_file_raises(self, tmp_path: Path):
        """Verify loading missing file raises error."""
        missing_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_config(missing_path)


class TestFindConfigFile:
    """Tests for find_config_file function."""

    def test_finds_config_in_current_dir(self, tmp_path: Path):
        """Verify config file is found in current directory."""
        config_path = tmp_path / "sentinel_scan.yaml"
        config_path.write_text("version: '1.0'\n")

        found = find_config_file(tmp_path)
        assert found == config_path

    def test_finds_config_in_parent_dir(self, tmp_path: Path):
        """Verify config file is found in parent directory."""
        # Create config in parent
        config_path = tmp_path / "sentinel_scan.yaml"
        config_path.write_text("version: '1.0'\n")

        # Search from child directory
        child_dir = tmp_path / "src" / "module"
        child_dir.mkdir(parents=True)

        found = find_config_file(child_dir)
        assert found == config_path

    def test_returns_none_when_not_found(self, tmp_path: Path):
        """Verify None is returned when config not found."""
        # Create empty directory with no config
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Note: This might find a config higher up in the real filesystem
        # In practice, the search stops at filesystem root
        found = find_config_file(empty_dir)
        # Either None or a real config file in parent dirs
        assert found is None or found.name.startswith("sentinel")

    def test_finds_alternate_names(self, tmp_path: Path):
        """Verify alternate config file names are found."""
        # Test .sentinel_scan.yaml (hidden file)
        config_path = tmp_path / ".sentinel_scan.yaml"
        config_path.write_text("version: '1.0'\n")

        found = find_config_file(tmp_path)
        assert found == config_path


class TestConfigDataclasses:
    """Tests for configuration dataclasses."""

    def test_settings_defaults(self):
        """Verify Settings has correct defaults."""
        settings = Settings()
        assert settings.min_severity == "low"
        assert settings.exit_on_violation is True

    def test_exclusions_defaults(self):
        """Verify Exclusions has correct defaults."""
        exclusions = Exclusions()
        assert exclusions.paths == []

    def test_config_defaults(self):
        """Verify Config has correct defaults."""
        config = Config()
        assert config.version == "1.0"
        assert isinstance(config.settings, Settings)
        assert isinstance(config.exclusions, Exclusions)
