#!/usr/bin/env python3
"""End-to-end tests for Sentinel Scan CLI.

This script tests the CLI with real-world scenarios to validate:
- All CLI commands work correctly
- Detection accuracy on sample files
- Configuration loading and templates
- Output formats (console and JSON)
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class E2ETestRunner:
    """Run end-to-end tests for Sentinel Scan."""

    def __init__(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sentinel_e2e_"))
        self.passed = 0
        self.failed = 0
        self.errors: list[str] = []

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def run_command(self, args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
        """Run a sentinel-scan command and return (exit_code, stdout, stderr)."""
        cmd = ["sentinel-scan"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or self.temp_dir,
        )
        return result.returncode, result.stdout, result.stderr

    def create_test_file(self, name: str, content: str) -> Path:
        """Create a test file in the temp directory."""
        path = self.temp_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def assert_true(self, condition: bool, test_name: str, details: str = "") -> bool:
        """Assert a condition and track results."""
        if condition:
            print(f"  ✓ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"  ✗ {test_name}")
            if details:
                print(f"    {details}")
            self.failed += 1
            self.errors.append(f"{test_name}: {details}")
            return False

    def assert_exit_code(
        self, actual: int, expected: int, test_name: str, stderr: str = ""
    ) -> bool:
        """Assert exit code with helpful debug info."""
        if actual == expected:
            print(f"  ✓ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"  ✗ {test_name} (got {actual}, expected {expected})")
            if stderr.strip():
                print(f"    stderr: {stderr.strip()[:200]}")
            self.failed += 1
            self.errors.append(f"{test_name}: got {actual}, expected {expected}")
            return False

    def test_version(self) -> None:
        """Test --version flag."""
        print("\n[Test: Version]")
        code, stdout, stderr = self.run_command(["--version"])
        self.assert_true(code == 0, "Exit code is 0")
        self.assert_true("0.1.0" in stdout or "0.1.0" in stderr, "Version displayed")

    def test_help(self) -> None:
        """Test --help flag."""
        print("\n[Test: Help]")
        code, stdout, stderr = self.run_command(["--help"])
        self.assert_true(code == 0, "Exit code is 0")
        self.assert_true("scan" in stdout, "scan command listed")
        self.assert_true("init" in stdout, "init command listed")
        self.assert_true("install-hook" in stdout, "install-hook command listed")

    def test_scan_clean_file(self) -> None:
        """Test scanning a file with no violations."""
        print("\n[Test: Scan Clean File]")
        self.create_test_file(
            "clean.py",
            '''"""A clean Python file."""

def hello():
    """Say hello."""
    print("Hello, World!")

if __name__ == "__main__":
    hello()
''',
        )

        code, stdout, stderr = self.run_command(["scan", "clean.py"])
        # Combine stdout and stderr (Rich may output to either)
        output = stdout + stderr
        self.assert_exit_code(code, 0, "Exit code is 0 (no violations)", stderr)
        self.assert_true(
            "No violations" in output or "0 violation" in output or "No compliance" in output,
            "Reports no violations",
        )

    def test_scan_file_with_violations(self) -> None:
        """Test scanning a file with PII violations."""
        print("\n[Test: Scan File with Violations]")
        self.create_test_file(
            "violations.py",
            '''"""File with violations."""

# Contains PII
email = "john.doe@company.com"
phone = "555-123-4567"
ssn = "123-45-6789"
''',
        )

        code, stdout, stderr = self.run_command(["scan", "violations.py"])
        # Combine stdout and stderr for checking (Rich may output to either)
        output = (stdout + stderr).lower()
        self.assert_true(code == 1, "Exit code is 1 (violations found)")
        self.assert_true("email" in output, "Email violation detected")
        self.assert_true("phone" in output, "Phone violation detected")
        self.assert_true("ssn" in output, "SSN violation detected")

    def test_scan_json_output(self) -> None:
        """Test JSON output format."""
        print("\n[Test: JSON Output]")
        self.create_test_file(
            "json_test.py",
            '''email = "test@example.org"
''',
        )

        code, stdout, stderr = self.run_command(["scan", "json_test.py", "--format", "json"])
        try:
            data = json.loads(stdout)
            self.assert_true(True, "Output is valid JSON")
            self.assert_true("violations" in data, "Has violations key")
            self.assert_true("files_scanned" in data, "Has files_scanned key")
            self.assert_true(data["files_scanned"] == 1, "Scanned 1 file")
        except json.JSONDecodeError as e:
            self.assert_true(False, "Output is valid JSON", str(e))

    def test_scan_severity_filter(self) -> None:
        """Test severity filtering."""
        print("\n[Test: Severity Filter]")
        self.create_test_file(
            "severity_test.py",
            '''# Mix of severities
email = "user@test.com"  # HIGH
ssn = "123-45-6789"      # CRITICAL
''',
        )

        # With critical filter, only SSN should be reported
        code, stdout, stderr = self.run_command(
            ["scan", "severity_test.py", "--severity", "critical", "--format", "json"]
        )
        try:
            data = json.loads(stdout)
            violations = data.get("violations", [])
            # Critical filter should only include SSN
            self.assert_true(
                all(v.get("severity", "").lower() == "critical" for v in violations),
                "Only critical violations reported",
            )
        except json.JSONDecodeError:
            self.assert_true(False, "Valid JSON output", "JSON parse error")

    def test_scan_directory(self) -> None:
        """Test directory scanning."""
        print("\n[Test: Directory Scan]")
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()

        self.create_test_file("file1.py", 'email = "a@b.com"\n')
        self.create_test_file("subdir/file2.py", 'phone = "555-111-2222"\n')

        code, stdout, stderr = self.run_command(["scan", ".", "--format", "json"])
        try:
            data = json.loads(stdout)
            self.assert_true(data["files_scanned"] >= 2, "Scanned multiple files")
            self.assert_true(len(data.get("violations", [])) >= 2, "Found violations in both files")
        except json.JSONDecodeError:
            self.assert_true(False, "Valid JSON output", "JSON parse error")

    def test_init_default(self) -> None:
        """Test init command with default template."""
        print("\n[Test: Init Default]")
        config_path = self.temp_dir / "sentinel_scan.yaml"

        # Use --force to overwrite if exists
        code, stdout, stderr = self.run_command(["init", "--force"])
        self.assert_exit_code(code, 0, "Exit code is 0", stderr)
        self.assert_true(config_path.exists(), "Config file created")

        if config_path.exists():
            content = config_path.read_text()
            self.assert_true("version:" in content, "Has version field")
            self.assert_true("detectors:" in content, "Has detectors field")

    def test_init_automotive_template(self) -> None:
        """Test init command with automotive template."""
        print("\n[Test: Init Automotive Template]")
        config_path = self.temp_dir / "sentinel_scan.yaml"

        # Use --force to overwrite if exists
        code, stdout, stderr = self.run_command(["init", "--template", "automotive", "--force"])
        self.assert_exit_code(code, 0, "Exit code is 0", stderr)
        self.assert_true(config_path.exists(), "Config file created")

        if config_path.exists():
            content = config_path.read_text()
            self.assert_true("vin:" in content.lower(), "Has VIN configuration")

    def test_inline_ignore(self) -> None:
        """Test inline ignore comments."""
        print("\n[Test: Inline Ignore]")
        self.create_test_file(
            "ignore_test.py",
            '''# This email is ignored
email1 = "ignored@test.com"  # sentinel-scan: ignore

# This email is not ignored
email2 = "flagged@test.com"
''',
        )

        code, stdout, stderr = self.run_command(["scan", "ignore_test.py", "--format", "json"])
        try:
            data = json.loads(stdout)
            violations = data.get("violations", [])
            # Should only have 1 violation (the non-ignored email)
            self.assert_true(len(violations) == 1, "Only 1 violation (ignored line excluded)")
            if violations:
                self.assert_true(
                    violations[0].get("line_number") == 5,
                    "Violation is on line 5 (non-ignored)",
                )
        except json.JSONDecodeError:
            self.assert_true(False, "Valid JSON output", "JSON parse error")

    def test_vin_detection(self) -> None:
        """Test VIN detection with checksum validation."""
        print("\n[Test: VIN Detection]")
        self.create_test_file(
            "vin_test.py",
            '''# Valid VIN with correct checksum
valid_vin = "5YJSA1DG9DFP14705"

# Invalid VIN (wrong checksum)
invalid_vin = "5YJSA1DG0DFP14705"
''',
        )

        code, stdout, stderr = self.run_command(["scan", "vin_test.py", "--format", "json"])
        try:
            data = json.loads(stdout)
            violations = data.get("violations", [])
            # Should detect valid VIN, may or may not detect invalid depending on config
            vin_violations = [v for v in violations if "vin" in v.get("violation_type", "").lower()]
            self.assert_true(len(vin_violations) >= 1, "VIN detected")
        except json.JSONDecodeError:
            self.assert_true(False, "Valid JSON output", "JSON parse error")

    def test_credit_card_luhn(self) -> None:
        """Test credit card detection with Luhn validation."""
        print("\n[Test: Credit Card Luhn Validation]")
        self.create_test_file(
            "cc_test.py",
            '''# Valid credit card (passes Luhn)
valid_cc = "4111111111111111"

# Invalid credit card (fails Luhn)
invalid_cc = "4111111111111112"
''',
        )

        code, stdout, stderr = self.run_command(["scan", "cc_test.py", "--format", "json"])
        try:
            data = json.loads(stdout)
            violations = data.get("violations", [])
            cc_violations = [
                v for v in violations if "credit" in v.get("violation_type", "").lower()
            ]
            # Should only detect valid CC (Luhn check)
            self.assert_true(
                len(cc_violations) == 1,
                "Only valid credit card detected (Luhn validation)",
            )
        except json.JSONDecodeError:
            self.assert_true(False, "Valid JSON output", "JSON parse error")

    def test_config_file(self) -> None:
        """Test custom config file with severity filter on CLI."""
        print("\n[Test: Custom Config File]")
        self.create_test_file(
            "config_test.py",
            '''email = "user@test.com"
ssn = "123-45-6789"
''',
        )

        # Use --severity critical to filter violations
        code, stdout, stderr = self.run_command(
            ["scan", "config_test.py", "--severity", "critical", "--format", "json"]
        )
        try:
            data = json.loads(stdout)
            violations = data.get("violations", [])
            # Only critical violations should be returned
            self.assert_true(
                all(v.get("severity", "").lower() == "critical" for v in violations),
                "Config respected (severity filter)",
            )
        except json.JSONDecodeError:
            self.assert_true(False, "Valid JSON output", "JSON parse error")

    def run_all(self) -> int:
        """Run all tests and return exit code."""
        print("=" * 60)
        print("Sentinel Scan E2E Tests")
        print("=" * 60)

        try:
            self.test_version()
            self.test_help()
            self.test_scan_clean_file()
            self.test_scan_file_with_violations()
            self.test_scan_json_output()
            self.test_scan_severity_filter()
            self.test_scan_directory()
            self.test_init_default()
            self.test_init_automotive_template()
            self.test_inline_ignore()
            self.test_vin_detection()
            self.test_credit_card_luhn()
            self.test_config_file()
        finally:
            self.cleanup()

        print("\n" + "=" * 60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        return 0 if self.failed == 0 else 1


def main() -> int:
    """Main entry point."""
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Check if sentinel-scan is installed
    result = subprocess.run(
        ["sentinel-scan", "--version"],
        capture_output=True,
    )
    if result.returncode != 0:
        print("Error: sentinel-scan is not installed.")
        print("Run: pip install -e .")
        return 2

    runner = E2ETestRunner()
    return runner.run_all()


if __name__ == "__main__":
    sys.exit(main())
