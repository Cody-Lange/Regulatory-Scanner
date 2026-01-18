# Sentinel Scan for VS Code

[![VS Code Marketplace](https://img.shields.io/badge/VS%20Code-Marketplace-blue.svg)](https://marketplace.visualstudio.com/items?itemName=sentinel-scan.sentinel-scan-vscode)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Real-time compliance scanning for Python code in VS Code.**

Catch data privacy violations (PII, VINs, sensitive data) as you type, before they ever reach your repository.

## Features

### Real-Time Diagnostics

- **Inline warnings** appear as you type with 300ms debounce
- **Severity-based highlighting**: Critical (red), High (yellow), Medium (blue), Low (gray)
- **Violation counts** displayed in the status bar

### Rich Information

- **Hover details** show the matched text, regulation, and recommended fix
- **Quick navigation** to violation locations
- **Respects your config** from `sentinel_scan.yaml`

### Detection Types

| Type | Description | Severity |
|------|-------------|----------|
| **Email** | Email addresses in code | High |
| **Phone** | US phone number formats | High |
| **SSN** | Social Security Numbers | Critical |
| **Credit Card** | Card numbers with Luhn validation | Critical |
| **VIN** | Vehicle IDs with checksum validation | High |

## Requirements

- **Python 3.11+** installed and available in PATH
- **sentinel-scan CLI** installed: `pip install sentinel-scan`

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Sentinel Scan"
4. Click Install

### From Source

```bash
# Clone the repository
git clone https://github.com/Cody-Lange/Regulatory-Scanner.git
cd Regulatory-Scanner/sentinel-scan-vscode

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Package extension
npm run package

# Install the .vsix file
code --install-extension sentinel-scan-0.1.0.vsix
```

## Usage

1. **Install the Python CLI**: `pip install sentinel-scan`
2. **Open a Python file** in VS Code
3. **Violations appear automatically** as inline diagnostics

### Example

When you write code like this:

```python
# This will show a warning
user_email = "john.doe@company.com"

# This will show a critical warning
ssn = "123-45-6789"

# This line is ignored
test_email = "test@example.com"  # sentinel-scan: ignore
```

You'll see:
- Yellow squiggly under `john.doe@company.com` (HIGH severity)
- Red squiggly under `123-45-6789` (CRITICAL severity)
- No warning on the ignored line

## Configuration

### Extension Settings

Configure in VS Code settings (`Ctrl+,` / `Cmd+,`):

| Setting | Default | Description |
|---------|---------|-------------|
| `sentinel-scan.enable` | `true` | Enable/disable the extension |
| `sentinel-scan.pythonPath` | `"python"` | Path to Python interpreter |
| `sentinel-scan.minSeverity` | `"low"` | Minimum severity to display |
| `sentinel-scan.scanOnSave` | `true` | Scan files when saved |
| `sentinel-scan.scanOnType` | `true` | Scan as you type (with debounce) |
| `sentinel-scan.debounceDelay` | `300` | Milliseconds to wait before scanning |
| `sentinel-scan.configPath` | `""` | Custom path to sentinel_scan.yaml |

### Project Configuration

Create a `sentinel_scan.yaml` in your project root:

```yaml
version: "1.0"

settings:
  min_severity: low

allowlist:
  - "example.com"
  - "regex:^test_"

exclusions:
  paths:
    - "*/tests/*"

detectors:
  pii:
    enabled: true
  vin:
    enabled: true
```

## Commands

Access via Command Palette (Ctrl+Shift+P / Cmd+Shift+P):

| Command | Description |
|---------|-------------|
| `Sentinel Scan: Scan Current File` | Manually scan the active file |
| `Sentinel Scan: Scan Workspace` | Scan all Python files in workspace |
| `Sentinel Scan: Clear Diagnostics` | Clear all diagnostics |
| `Sentinel Scan: Show Output` | Show the output channel |

## Inline Ignore Comments

Suppress warnings for specific lines:

```python
# Ignore all detectors
email = "admin@company.com"  # sentinel-scan: ignore

# Ignore specific detector
vin = "5YJSA1DG9DFP14705"  # sentinel-scan: ignore vin

# Ignore multiple detectors
data = "user@test.com 555-1234"  # sentinel-scan: ignore email, phone
```

## Troubleshooting

### Extension Not Working

1. **Check Python is installed**: Run `python --version` in terminal
2. **Check CLI is installed**: Run `sentinel-scan --version`
3. **Check Output channel**: View > Output > Select "Sentinel Scan"
4. **Reload window**: Command Palette > "Developer: Reload Window"

### High CPU Usage

1. Increase `sentinel-scan.debounceDelay` to 500 or higher
2. Disable `sentinel-scan.scanOnType` and use `scanOnSave` only
3. Add large directories to `exclusions.paths` in config

### False Positives

1. Add patterns to `allowlist` in `sentinel_scan.yaml`
2. Use inline ignore comments for specific lines
3. Configure detector settings in your config file

## Architecture

The extension uses a bridge architecture:

```
VS Code Extension (TypeScript)
        |
        v
   JSON over stdio
        |
        v
Python Bridge Process (sentinel-scan)
        |
        v
   Detection Engine
```

- **One bridge process** per VS Code window
- **30-second timeout** for scan requests
- **300ms debounce** for real-time scanning

## Development

### Setup

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run linter
npm run lint

# Run tests
npm test
```

### Debugging

1. Open this folder in VS Code
2. Press F5 to launch Extension Development Host
3. Open a Python file in the new window
4. Check the Debug Console for logs

### Building

```bash
# Package for distribution
npm run package

# Creates sentinel-scan-0.1.0.vsix
```

### Publishing

```bash
# Login to VS Code Marketplace
vsce login <publisher>

# Publish extension
npm run publish
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test`
5. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Cody-Lange/Regulatory-Scanner/issues)
- **Documentation**: [sentinelscan.app](https://sentinelscan.app)

---

Part of the [Sentinel Scan](https://github.com/Cody-Lange/Regulatory-Scanner) project.
