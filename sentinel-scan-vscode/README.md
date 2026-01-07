# Sentinel Scan VS Code Extension

Developer-native compliance scanning for LLM applications.

## Features

- **Real-time scanning**: Get inline warnings as you type
- **Hover information**: See violation details, regulations, and fixes
- **Quick fixes**: Apply fixes with one click
- **Status bar**: See violation count at a glance

## Installation

1. Install the Sentinel Scan Python package:
   ```bash
   pip install sentinel-scan
   ```

2. Install this extension from VS Code Marketplace (coming soon)

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `sentinel-scan.enable` | `true` | Enable/disable the extension |
| `sentinel-scan.pythonPath` | `"python"` | Path to Python interpreter |
| `sentinel-scan.minSeverity` | `"low"` | Minimum severity to show |
| `sentinel-scan.scanOnSave` | `true` | Scan files on save |
| `sentinel-scan.scanOnType` | `true` | Scan as you type |
| `sentinel-scan.debounceDelay` | `300` | Debounce delay in ms |

## Commands

- **Sentinel Scan: Scan Current File** - Scan the active file
- **Sentinel Scan: Scan Workspace** - Scan all Python files in workspace

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run tests
npm test
```

## License

MIT
