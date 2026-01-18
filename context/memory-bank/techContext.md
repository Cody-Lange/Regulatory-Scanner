# Technical Context

## Technology Stack

### Core Engine (Python)
| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13.4 | Runtime |
| Typer | >=0.9.0 | CLI framework |
| PyYAML | >=6.0 | Configuration |
| Rich | >=13.0 | Console output |

### Development Tools (Python)
| Tool | Version | Purpose |
|------|---------|---------|
| pytest | >=7.0 | Testing |
| pytest-cov | >=4.0 | Coverage |
| mypy | >=1.0 | Type checking |
| ruff | >=0.1.0 | Linting/formatting |

### VS Code Extension (TypeScript)
| Component | Version | Purpose |
|-----------|---------|---------|
| TypeScript | >=5.0 | Language |
| VS Code API | Latest | Extension SDK |
| Node.js | >=18 | Runtime |

### Frontend (Landing Page - Already Built)
| Component | Version | Purpose |
|-----------|---------|---------|
| React | 18.3.1 | UI framework |
| Vite | 6.0.5 | Build tool |
| Tailwind CSS | 3.4.17 | Styling |
| Framer Motion | 11.15.0 | Animations |

---

## Environment Requirements

### Development
- Python 3.13.4
- Node.js 18 or higher
- VS Code 1.85 or higher (for extension testing)
- Git

### Production
- Python 3.13+ (user's environment)
- VS Code 1.80+ (for extension users)
- No external services required (all local processing)

---

## Package Distribution

### Python Package
- **Registry:** PyPI
- **Package Name:** `sentinel-scan`
- **Install:** `pip install sentinel-scan`

### VS Code Extension
- **Registry:** VS Code Marketplace
- **Extension ID:** `sentinel-scan.sentinel-scan`
- **Install:** VS Code Extensions panel

---

## Key Technical Decisions

1. **Python `ast` module** for parsing (no external parser dependencies)
2. **Subprocess model** for VS Code ↔ Python communication
3. **YAML configuration** for human-readable, version-controllable config
4. **Rich library** for beautiful console output
5. **No telemetry** in MVP (privacy-first approach)
6. **Regex allowlists** - `regex:` prefix for pattern matching, literal otherwise
7. **AllowlistMatcher class** - separates literal/regex patterns for performance

---

## File Encoding
- Default: UTF-8
- Fallback: Latin-1 for legacy files
- Skip binary files automatically

## Performance Targets
| Metric | Target | Stretch |
|--------|--------|---------|
| VS Code diagnostics | <500ms | <200ms |
| CLI scan | <1s/1K lines | <0.5s/1K lines |
| Memory usage | <100MB | <50MB |
| False positive rate | <5% | <2% |
