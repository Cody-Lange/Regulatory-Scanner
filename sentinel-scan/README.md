# Sentinel Scan

[![CI](https://github.com/Cody-Lange/Regulatory-Scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/Cody-Lange/Regulatory-Scanner/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Developer-native compliance scanning for LLM applications.**

Sentinel Scan detects data privacy violations (PII, VINs, sensitive data) in Python code before deployment. It integrates seamlessly into your IDE (VS Code) and CI/CD workflows.

## Features

- **PII Detection**: Email, phone numbers, SSN, credit cards (with Luhn validation)
- **VIN Detection**: Vehicle Identification Numbers with checksum validation
- **Context-Aware**: AST-based analysis reduces false positives in tests and comments
- **Regex Allowlists**: Flexible pattern matching with literal and regex support
- **Industry Templates**: Pre-configured for automotive and other industries
- **VS Code Extension**: Real-time inline diagnostics as you type
- **CI/CD Ready**: JSON output, exit codes, and pre-commit hooks

## Quick Start

### Installation

```bash
# From PyPI (recommended)
pip install sentinel-scan

# From source
git clone https://github.com/Cody-Lange/Regulatory-Scanner.git
cd Regulatory-Scanner/sentinel-scan
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Scan a directory
sentinel-scan scan ./src

# Scan with JSON output for CI/CD
sentinel-scan scan ./src --format json

# Filter by severity (low, medium, high, critical)
sentinel-scan scan ./src --severity high

# Initialize a config file
sentinel-scan init

# Use an industry template
sentinel-scan init --template automotive

# Install git pre-commit hook
sentinel-scan install-hook
```

## CLI Commands

### `sentinel-scan scan`

Scan files or directories for compliance violations.

```bash
sentinel-scan scan <PATH> [OPTIONS]

Options:
  --format [console|json]  Output format (default: console)
  --severity [low|medium|high|critical]  Minimum severity to report
  --config PATH            Path to config file
  --recursive / --no-recursive  Scan directories recursively (default: true)
  --verbose               Enable verbose output
```

**Exit Codes:**
- `0` - No violations found
- `1` - Violations found
- `2` - Error occurred

### `sentinel-scan init`

Generate a configuration file.

```bash
sentinel-scan init [OPTIONS]

Options:
  --template [default|automotive]  Template to use
  --output PATH                    Output file path
  --force                          Overwrite existing file
```

### `sentinel-scan install-hook`

Install a git pre-commit or pre-push hook.

```bash
sentinel-scan install-hook [OPTIONS]

Options:
  --type [pre-commit|pre-push]  Hook type (default: pre-commit)
  --git-dir PATH                Path to .git directory
```

## Configuration

Create a `sentinel_scan.yaml` in your project root:

```yaml
version: "1.0"

settings:
  min_severity: low          # low, medium, high, critical
  exit_on_violation: true    # Exit with code 1 if violations found

# Allowlist patterns - text matching these won't be flagged
# Supports both literal (substring) and regex patterns
allowlist:
  # Literal patterns (substring match)
  - "example.com"            # Matches user@example.com
  - "test@"                  # Matches test@anything.com
  - "555-0100"               # US fictional phone prefix

  # Regex patterns (prefix with "regex:")
  - "regex:^noreply@"        # Emails starting with noreply@
  - "regex:@(test|example)\\."  # Test domain emails
  - "regex:\\+1-555-\\d{3}-\\d{4}"  # Fictional US phone numbers

# File and path exclusions (glob patterns)
exclusions:
  paths:
    - "*/tests/*"
    - "*/.venv/*"
    - "*/.git/*"
    - "*/__pycache__/*"

# Detector configurations
detectors:
  pii:
    enabled: true
    patterns:
      email:
        enabled: true
        severity: high
      phone:
        enabled: true
        severity: high
      ssn:
        enabled: true
        severity: critical
      credit_card:
        enabled: true
        severity: critical

  vin:
    enabled: true
    validate_checksum: true   # Only flag VINs with valid checksums
```

### Regex Pattern Examples

```yaml
allowlist:
  # Match auto-generated emails
  - "regex:^(noreply|no-reply|donotreply)@"

  # Match test/staging domains
  - "regex:@.*\\.(test|local|internal)$"

  # Match specific phone patterns
  - "regex:^\\+1-555-"

  # Match VIN prefixes (manufacturer codes)
  - "regex:^(5YJ|1G1|WVW)"  # Tesla, GM, VW
```

## Inline Ignores

Disable scanning for specific lines:

```python
# Ignore all detectors on this line
email = "admin@company.com"  # sentinel-scan: ignore

# Ignore specific detector types
vin = "5YJSA1DG9DFP14705"  # sentinel-scan: ignore vin
contact = "user@test.com"  # sentinel-scan: ignore email, phone
```

## VS Code Extension

The Sentinel Scan VS Code extension provides real-time diagnostics as you type.

### Installation

1. Install the Python CLI: `pip install sentinel-scan`
2. Install the VS Code extension from the Marketplace (or build from source)
3. Open a Python file - violations appear as inline warnings

### Features

- Real-time scanning with 300ms debounce
- Severity-based diagnostic levels
- Status bar violation count
- Works with your project's `sentinel_scan.yaml`

## CI/CD Integration

### GitHub Actions

```yaml
name: Compliance Check

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install sentinel-scan
        run: pip install sentinel-scan

      - name: Run compliance scan
        run: sentinel-scan scan ./src --severity high
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: sentinel-scan
        name: Sentinel Scan
        entry: sentinel-scan scan
        language: system
        types: [python]
        pass_filenames: true
```

Or use the built-in hook installer:

```bash
sentinel-scan install-hook
```

## API Usage

```python
from sentinel_scan.scanner import Scanner
from sentinel_scan.config import get_default_config

# Create scanner with default config
config = get_default_config()
scanner = Scanner(config)

# Scan source code
result = scanner.scan_source('''
email = "user@company.com"
vin = "5YJSA1DG9DFP14705"
''', "example.py")

print(f"Found {result.violation_count} violations")
for violation in result.violations:
    print(f"  Line {violation.line_number}: {violation.violation_type}")
    print(f"    {violation.message}")
    print(f"    Recommendation: {violation.recommendation}")
```

### Using Allowlist Matcher

```python
from sentinel_scan.allowlist import AllowlistMatcher

matcher = AllowlistMatcher([
    "example.com",           # Literal match
    "regex:^test_.*@",       # Regex match
])

matcher.is_allowlisted("user@example.com")    # True
matcher.is_allowlisted("test_bot@foo.com")    # True
matcher.is_allowlisted("admin@company.com")   # False
```

## Detectors

### PII Detector

| Type | Pattern | Severity | Regulation |
|------|---------|----------|------------|
| Email | Standard email format | HIGH | GDPR, CCPA |
| Phone | US formats (+1, parentheses, dashes) | HIGH | GDPR, TCPA |
| SSN | XXX-XX-XXXX with validation | CRITICAL | CCPA, HIPAA |
| Credit Card | 13-19 digits with Luhn validation | CRITICAL | PCI-DSS |

### VIN Detector

| Type | Pattern | Severity | Regulation |
|------|---------|----------|------------|
| VIN | 17 alphanumeric (no I, O, Q) | HIGH | GDPR, DPPA |

VIN detection includes checksum validation to reduce false positives.

## Development

```bash
# Clone the repository
git clone https://github.com/Cody-Lange/Regulatory-Scanner.git
cd Regulatory-Scanner/sentinel-scan

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=sentinel_scan --cov-report=term-missing

# Type checking
mypy sentinel_scan

# Linting and formatting
ruff check sentinel_scan tests
ruff format sentinel_scan tests
```

## Project Structure

```
sentinel-scan/
├── sentinel_scan/
│   ├── __init__.py
│   ├── cli.py              # CLI commands
│   ├── scanner.py          # Scanner orchestrator
│   ├── config.py           # Configuration loading
│   ├── models.py           # Data models
│   ├── allowlist.py        # Regex/literal pattern matching
│   ├── detection/
│   │   ├── base.py         # Detector ABC
│   │   ├── registry.py     # Detector registry
│   │   ├── context_analyzer.py  # AST analysis
│   │   ├── pii_detector.py # PII detection
│   │   └── vin_detector.py # VIN detection
│   ├── rules/
│   │   └── engine.py       # Rule filtering
│   ├── formatters/
│   │   ├── console.py      # Rich console output
│   │   └── json_output.py  # JSON output
│   └── templates/
│       ├── default.yaml    # Default config
│       └── automotive.yaml # Automotive template
└── tests/
    ├── unit/               # Unit tests
    └── integration/        # Integration tests
```

## Output Examples

### Console Output

```
╭──────────────────────────────── Sentinel Scan ────────────────────────────────╮
│ [!!] 3 compliance violation(s) found                                          │
╰───────────────────────────────────────────────────────────────────────────────╯

/path/to/file.py
  Line 5: EMAIL - Email address detected in source code
    Matched: user....com
    Regulation: GDPR Article 6, CCPA
    Tip: Hash or remove email before sending to LLM.

  Line 8: SSN - Social Security Number detected in source code
    Matched: 123-...6789
    Regulation: CCPA, State Privacy Laws
    Tip: CRITICAL: Remove SSN immediately. Never include in LLM prompts.

┏━━━━━━━━━━┳━━━━━━━┓
┃ Severity ┃ Count ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ Critical │     1 │
│ High     │     1 │
│ Medium   │     1 │
│ Low      │     0 │
└──────────┴───────┘
```

### JSON Output

```json
{
  "files_scanned": 1,
  "lines_scanned": 25,
  "violation_count": 2,
  "violations": [
    {
      "file_path": "/path/to/file.py",
      "line_number": 5,
      "column_number": 10,
      "detector": "pii",
      "violation_type": "email",
      "matched_text": "user....com",
      "severity": "HIGH",
      "regulation": "GDPR Article 6, CCPA",
      "message": "Email address detected in source code",
      "recommendation": "Hash or remove email before sending to LLM."
    }
  ],
  "summary": {
    "critical": 0,
    "high": 1,
    "medium": 1,
    "low": 0
  }
}
```

## Performance

Sentinel Scan is optimized for speed:

| Metric | Target | Actual |
|--------|--------|--------|
| Per-file scan | <500ms | ~50-100ms |
| 1000 lines of code | <1s | ~200ms |
| Memory usage (50K lines) | <100MB | ~30MB |

### Optimization Tips

- Use `--severity high` to skip low-severity checks
- Add large directories to `exclusions.paths`
- Use allowlists to skip known-good patterns
- For CI/CD, scan only changed files

## Troubleshooting

### Common Issues

**"command not found: sentinel-scan"**
```bash
# Ensure pip installed to PATH
pip install --user sentinel-scan
# Or use full path
python -m sentinel_scan.cli scan ./src
```

**"UnicodeDecodeError" on Windows**
```bash
# Set UTF-8 encoding
set PYTHONIOENCODING=utf-8
sentinel-scan scan ./src
```

**High false positive rate**
1. Add common patterns to allowlist
2. Use `sentinel-scan init` for sensible defaults
3. Add inline ignore comments for intentional exceptions

**Slow scanning**
1. Exclude virtual environments: `*/.venv/*`
2. Exclude test directories: `*/tests/*`
3. Use `--severity high` for faster scans

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Ensure code quality (`ruff check && mypy sentinel_scan`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Support

- **Issues**: [GitHub Issues](https://github.com/Cody-Lange/Regulatory-Scanner/issues)
- **Documentation**: [sentinelscan.app](https://sentinelscan.app)
- **Email**: support@sentinelscan.app

---

Built with care for developers who care about compliance.
