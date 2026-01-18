# Sentinel Scan

[![CI](https://github.com/Cody-Lange/Regulatory-Scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/Cody-Lange/Regulatory-Scanner/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Developer-native compliance scanning for LLM applications.** Catch data privacy violations before they cost millions.

Sentinel Scan detects PII (emails, phone numbers, SSNs, credit cards), VINs, and other sensitive data in Python code before deployment. It integrates seamlessly into your IDE (VS Code) and CI/CD workflows to prevent compliance violations from reaching production.

## Why Sentinel Scan?

- **Prevent costly breaches**: GDPR fines can reach 4% of global revenue
- **Shift left on compliance**: Catch issues in development, not production
- **Developer-friendly**: Works in your IDE with real-time feedback
- **Low false positives**: AST-based context analysis understands your code
- **Regulatory mapping**: Know exactly which regulations apply (GDPR, CCPA, HIPAA, PCI-DSS)

## Quick Start

```bash
# Install the CLI
pip install sentinel-scan

# Scan your code
sentinel-scan scan ./src

# Initialize config with automotive template
sentinel-scan init --template automotive

# Install pre-commit hook
sentinel-scan install-hook
```

## Project Components

This monorepo contains three main components:

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **[sentinel-scan](./sentinel-scan/)** | Python CLI and detection engine | [README](./sentinel-scan/README.md) |
| **[sentinel-scan-vscode](./sentinel-scan-vscode/)** | VS Code extension for real-time scanning | [README](./sentinel-scan-vscode/README.md) |
| **[frontend](./frontend/)** | Landing page at sentinelscan.app | [README](./frontend/README.md) |

## Features

### Detection Capabilities

| Type | Examples | Validation | Severity |
|------|----------|------------|----------|
| **Email** | user@company.com | Format validation | HIGH |
| **Phone** | +1 (555) 123-4567 | US format patterns | HIGH |
| **SSN** | 123-45-6789 | Format + range validation | CRITICAL |
| **Credit Card** | 4111-1111-1111-1111 | Luhn checksum | CRITICAL |
| **VIN** | 5YJSA1DG9DFP14705 | ISO checksum validation | HIGH |

### Context-Aware Analysis

Sentinel Scan uses AST (Abstract Syntax Tree) analysis to understand code context:

- **Reduces false positives** in test files and fixtures
- **Skips docstrings and comments** (configurable)
- **Detects data flowing to LLM APIs** and elevates severity
- **Respects inline ignore comments** for intentional exceptions

### Flexible Allowlists

```yaml
allowlist:
  # Literal patterns (substring match)
  - "example.com"
  - "555-0100"              # US fictional phone prefix

  # Regex patterns
  - "regex:^noreply@"       # Auto-generated emails
  - "regex:@(test|staging)\\." # Test domains
```

## Installation

### Python CLI

```bash
# From PyPI
pip install sentinel-scan

# From source
git clone https://github.com/Cody-Lange/Regulatory-Scanner.git
cd Regulatory-Scanner/sentinel-scan
pip install -e ".[dev]"
```

### VS Code Extension

1. Install the Python CLI: `pip install sentinel-scan`
2. Install extension from VS Code Marketplace (or build from source)
3. Open a Python file - violations appear as inline warnings

## Usage Examples

### Command Line

```bash
# Basic scan
sentinel-scan scan ./src

# JSON output for CI/CD
sentinel-scan scan ./src --format json

# Filter by severity
sentinel-scan scan ./src --severity high

# With custom config
sentinel-scan scan ./src --config sentinel_scan.yaml
```

### Python API

```python
from sentinel_scan.scanner import Scanner
from sentinel_scan.config import get_default_config

config = get_default_config()
scanner = Scanner(config)

result = scanner.scan_source('''
email = "user@company.com"
vin = "5YJSA1DG9DFP14705"
''', "example.py")

for violation in result.violations:
    print(f"{violation.violation_type}: {violation.message}")
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Run compliance scan
  run: sentinel-scan scan ./src --severity high
```

## Configuration

Create `sentinel_scan.yaml` in your project root:

```yaml
version: "1.0"

settings:
  min_severity: low
  exit_on_violation: true

allowlist:
  - "example.com"
  - "regex:^test_"

exclusions:
  paths:
    - "*/tests/*"
    - "*/.venv/*"

detectors:
  pii:
    enabled: true
  vin:
    enabled: true
    validate_checksum: true
```

## Project Structure

```
Regulatory-Scanner/
├── sentinel-scan/           # Python CLI and detection engine
│   ├── sentinel_scan/       # Source code
│   ├── tests/               # Unit and integration tests
│   └── README.md
├── sentinel-scan-vscode/    # VS Code extension
│   ├── src/                 # TypeScript source
│   └── README.md
├── frontend/                # Landing page (React + Tailwind)
│   ├── src/
│   └── README.md
└── context/                 # Project documentation
    ├── PLAN.md              # Development roadmap
    ├── CLAUDE.md            # Development rules
    └── memory-bank/         # Project context files
```

## Development

### Prerequisites

- Python 3.11+
- Node.js 18+ (for VS Code extension and frontend)

### Setup

```bash
# Clone repository
git clone https://github.com/Cody-Lange/Regulatory-Scanner.git
cd Regulatory-Scanner

# Setup Python CLI
cd sentinel-scan
pip install -e ".[dev]"
pytest  # Run tests

# Setup VS Code extension
cd ../sentinel-scan-vscode
npm install
npm run compile

# Setup frontend
cd ../frontend
npm install
npm run dev
```

### Running Tests

```bash
# Python tests with coverage
cd sentinel-scan
pytest --cov=sentinel_scan --cov-report=term-missing

# E2E tests
python scripts/e2e_test.py

# Type checking
mypy sentinel_scan

# Linting
ruff check sentinel_scan tests
```

## Roadmap

- [x] **Phase 1**: Core detection engine (PII, VIN)
- [x] **Phase 2**: CLI with scan, init, install-hook commands
- [x] **Phase 3**: VS Code extension with real-time scanning
- [x] **Phase 4**: False positive management (regex allowlists)
- [x] **Phase 5**: Industry templates (automotive, healthcare)
- [x] **Phase 6**: Documentation and deployment
- [ ] **Phase 7**: PHI detection for healthcare
- [ ] **Phase 8**: SARIF output format
- [ ] **Phase 9**: Custom detector plugins

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest && ruff check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Cody-Lange/Regulatory-Scanner/issues)
- **Documentation**: [sentinelscan.app](https://sentinelscan.app)
- **Email**: support@sentinelscan.app

---

Built with care for developers who care about compliance.
