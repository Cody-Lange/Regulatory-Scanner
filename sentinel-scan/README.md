# Sentinel Scan

Developer-native compliance scanning for LLM applications.

## Overview

Sentinel Scan detects data privacy violations (PII, VINs, PHI) in Python code before deployment. It integrates into your IDE (VS Code) and CI/CD workflows.

## Installation

```bash
# Install from source (development)
pip install -e ".[dev]"
```

## Usage

### CLI

```bash
# Scan a directory
sentinel-scan scan ./src

# Scan with JSON output
sentinel-scan scan ./src --format json

# Filter by severity
sentinel-scan scan ./src --severity high

# Initialize config file
sentinel-scan init
```

### VS Code Extension

Install the Sentinel Scan extension from VS Code Marketplace (coming soon).

## Configuration

Create a `sentinel_scan.yaml` in your project root:

```yaml
version: "1.0"

settings:
  min_severity: low
  exit_on_violation: true

allowlist:
  - "example.com"
  - "test@"

exclusions:
  paths:
    - "*/tests/*"
    - "*/.venv/*"

detectors:
  pii:
    enabled: true
    patterns:
      email:
        enabled: true
        severity: high
  vin:
    enabled: true
    validate_checksum: true
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=sentinel_scan --cov-report=term-missing

# Type checking
mypy sentinel_scan

# Linting
ruff check sentinel_scan tests

# Format code
ruff format sentinel_scan tests
```

## License

MIT
