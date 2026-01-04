# SENTINEL SCAN - TECHNICAL SPECIFICATION v2.0
**Last Updated:** January 2, 2026  
**Status:** MVP Specification  
**Target Completion:** Week 5, January 2026

---

## REVISION SUMMARY (v2.0)

Key changes from v1.0:
- **VS Code extension → P0** (demo-critical for enterprise sales)
- **AST context analysis → P0** (differentiates from "just a linter")
- **False positive management → P0** (developers disable noisy tools)
- **LLM API flow detection added** (prioritizes violations reaching APIs)
- **Timeline extended** to 5 weeks (includes validation week)

---

## 1. SYSTEM OVERVIEW

### Purpose
Static code analysis tool detecting data privacy violations in Python LLM applications before deployment.

### Design Principles
1. **Developer-First:** VS Code inline warnings; seamless workflow
2. **Fast & Accurate:** <500ms diagnostics; <5% false positive rate
3. **Context-Aware:** AST analysis distinguishes test vs production; identifies LLM API flows
4. **Actionable:** Clear messages with line numbers, regulations, and fixes

### MVP Scope

| Priority | Feature | Rationale |
|----------|---------|-----------|
| **P0** | VS Code Extension | Demo-critical; inline warnings as devs type |
| **P0** | CLI Scanner | CI/CD integration, pre-commit hooks |
| **P0** | PII Detection | Core value (email, phone, SSN, address) |
| **P0** | VIN Detection | Automotive differentiator |
| **P0** | AST Context Analysis | Distinguishes us from grep |
| **P0** | False Positive Management | Table stakes for adoption |
| **P1** | Pre-commit Hook | Developer workflow |
| **P1** | JSON Audit Export | Compliance requirement |

**Out of Scope:** Web dashboard, CI/CD integrations, ML detection, multi-language support.

---

## 2. ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────┐
│                      SENTINEL SCAN                             │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐              ┌──────────────────┐       │
│  │  VS Code Plugin  │              │    CLI Tool      │       │
│  │  (TypeScript)    │              │    (Python)      │       │
│  │                  │              │                  │       │
│  │ • Inline squiggles│             │ • Batch scanning │       │
│  │ • Hover info     │              │ • Pre-commit     │       │
│  │ • Quick fixes    │              │ • JSON output    │       │
│  └────────┬─────────┘              └────────┬─────────┘       │
│           │                                 │                  │
│           └────────────┬────────────────────┘                  │
│                        ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              DETECTION ENGINE (Python)                   │  │
│  │                                                          │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────────────┐  │  │
│  │  │   Regex     │ │    AST      │ │     Context       │  │  │
│  │  │  Detectors  │ │   Parser    │ │    Analyzer       │  │  │
│  │  │ PII, VIN    │ │             │ │ Test detection,   │  │  │
│  │  │             │ │             │ │ LLM API flows     │  │  │
│  │  └─────────────┘ └─────────────┘ └───────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                        │                                       │
│                        ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    RULE ENGINE                           │  │
│  │  YAML Config │ Industry Templates │ Allowlists/Ignores  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Communication
- **VS Code ↔ Engine:** Subprocess; file content via stdin, JSON violations via stdout
- **CLI ↔ Engine:** Direct Python function calls

---

## 3. VS CODE EXTENSION

### Features

**1. Inline Diagnostics**
- Red/yellow squiggles under violations
- Updates on keystroke (300ms debounce)

**2. Hover Information**
```
⚠️ PII Detected: Email Address
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Severity: HIGH
Regulation: GDPR Article 6, CCPA §1798.100

💡 Fix: Hash or remove before sending to LLM
```

**3. Quick Fixes**
- "Add to allowlist"
- "Ignore this line" (`# sentinel-scan: ignore`)
- "Ignore this violation type"

**4. Status Bar**
- `Sentinel Scan: ✓ Clean` or `Sentinel Scan: 3 violations`

### Implementation Structure

```
sentinel-scan-vscode/
├── package.json
├── src/
│   ├── extension.ts      # Activation, event handlers
│   ├── diagnostics.ts    # Diagnostic provider
│   ├── scanner.ts        # Python subprocess wrapper
│   └── codeActions.ts    # Quick fix providers
└── python/
    └── scan_file.py      # Standalone scanner
```

### Key Code: Diagnostics Provider

```typescript
export class SentinelScanDiagnostics {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private debounceTimers: Map<string, NodeJS.Timeout> = new Map();
    
    async scanDocument(document: vscode.TextDocument) {
        const violations = await this.runScanner(document.getText());
        
        const diagnostics = violations.map(v => {
            const diagnostic = new vscode.Diagnostic(
                new vscode.Range(v.line - 1, v.column, v.line - 1, v.endColumn),
                `${v.type}: ${v.message}`,
                this.severityToVscode(v.severity)
            );
            diagnostic.source = 'Sentinel Scan';
            return diagnostic;
        });
        
        this.diagnosticCollection.set(document.uri, diagnostics);
    }
    
    private async runScanner(content: string): Promise<Violation[]> {
        // Spawn Python subprocess, pass content via stdin
        // Return parsed JSON violations
    }
}
```

---

## 4. CLI TOOL

### Commands

```bash
sentinel-scan scan ./src                    # Scan directory
sentinel-scan scan ./src --format json      # JSON output
sentinel-scan scan ./src --severity high    # Filter severity
sentinel-scan install-hook                  # Git pre-commit hook
```

### Console Output Example

```
┌─────────────────────────────────────────┐
│ ✗ 3 compliance violation(s) found       │
└─────────────────────────────────────────┘

src/analytics.py
  Line 47: EMAIL - Email address detected
    Matched: user@example...
    Regulation: GDPR Article 6
    💡 Hash or remove before sending to LLM

  Line 52: VIN - Vehicle Identification Number detected
    Matched: 1HGCM82633A...
    Regulation: GDPR (indirect identifier)
    💡 Remove or hash VIN before sending to LLM
```

---

## 5. DETECTION ENGINE

### Detector Interface

```python
class Detector(ABC):
    @abstractmethod
    def scan(self, source: str, tree: ast.AST, context: ContextAnalysis) -> List[Violation]:
        pass
```

### PII Detector Patterns

| Type | Pattern | Severity | Regulation |
|------|---------|----------|------------|
| Email | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}` | HIGH | GDPR Art 6, CCPA |
| Phone | `(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}` | HIGH | GDPR Art 6 |
| SSN | `\d{3}-\d{2}-\d{4}` | CRITICAL | CCPA, HIPAA |
| Credit Card | `4[0-9]{12}(?:[0-9]{3})?` (+ others) | CRITICAL | PCI-DSS |

### VIN Detector
- Pattern: `[A-HJ-NPR-Z0-9]{17}` (17 chars, no I/O/Q)
- Checksum validation to reduce false positives
- Severity: CRITICAL (can identify vehicle owners)

---

## 6. CONTEXT ANALYZER (KEY DIFFERENTIATOR)

The Context Analyzer uses AST analysis to understand code context—this is what differentiates us from "just grep."

### What It Detects

| Context | Detection Method | Impact |
|---------|------------------|--------|
| Test files | Path patterns (`/tests/`, `test_*.py`) | Lower severity |
| Test functions | Function name (`test_*`, `*_test`) | Lower severity |
| Comments | Line parsing | Ignore violations |
| Docstrings | AST node type | Ignore violations |
| LLM API calls | AST pattern matching | Elevate severity |
| Inline ignores | Comment parsing | Skip violation |

### LLM API Detection

Recognizes common patterns:
```python
LLM_API_PATTERNS = [
    'openai.chat.completions.create',
    'openai.completions.create', 
    'anthropic.messages.create',
    'client.chat.completions.create',
    'langchain',
]
```

### Severity Elevation Logic

```python
# Base severity from detector
severity = pattern_config['severity']

# Reduce for test context
if context.is_test_file or context.is_in_test_function(line):
    severity = Severity.LOW

# Elevate if flows to LLM API
elif context.flows_to_llm_api(line, matched_text):
    if severity == Severity.HIGH:
        severity = Severity.CRITICAL
```

---

## 7. FALSE POSITIVE MANAGEMENT

### Configuration Allowlists

```yaml
# sentinel_scan.yaml
allowlist:
  - "example.com"
  - "test@"
  - "555-0100"      # Test phone numbers

detectors:
  pii:
    patterns:
      email:
        allowlist:
          - "@example.com"
          - "@test.local"
```

### Inline Ignore Comments

```python
email = "real@example.com"  # sentinel-scan: ignore
test_email = "t@t.com"      # sentinel-scan: ignore email
data = {"a": 1}             # sentinel-scan: ignore email,phone
```

### File Exclusions

```yaml
exclusions:
  paths:
    - "*/tests/*"
    - "*/.venv/*"
    - "*/fixtures/*"
```

---

## 8. CONFIGURATION

### Full Schema

```yaml
version: "1.0"

settings:
  min_severity: "low"        # low, medium, high, critical
  exit_on_violation: true

allowlist:
  - "example.com"

exclusions:
  paths:
    - "*/tests/*"

detectors:
  pii:
    enabled: true
    patterns:
      email:
        enabled: true
        severity: "high"
        allowlist: ["@example.com"]
      ssn:
        enabled: true
        severity: "critical"
  
  vin:
    enabled: true
    validate_checksum: true
  
  custom:
    patterns:
      - name: "internal_id"
        pattern: 'CUST-\d{6}'
        severity: "medium"
        regulation: "Internal Policy"
        message: "Internal customer ID detected"
```

### Industry Templates

**Automotive** (`templates/automotive.yaml`):
- VIN detection (critical)
- Dealer codes
- Service record IDs

**Healthcare** (`templates/healthcare.yaml`, Phase 2):
- Medical Record Numbers
- NPI (National Provider Identifier)
- ICD-10 codes

---

## 9. DATA MODELS

```python
class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Violation:
    file_path: str
    line_number: int
    column_number: int
    end_column: int
    detector: str
    violation_type: str
    matched_text: str
    severity: Severity
    regulation: str
    message: str
    recommendation: str
    context_info: Dict[str, Any]

@dataclass  
class ScanResult:
    files_scanned: int
    lines_scanned: int
    violations: List[Violation]
    scan_duration_ms: int
    timestamp: str
```

---

## 10. TECH STACK

| Component | Technology | Rationale |
|-----------|------------|-----------|
| CLI | Python 3.11+ / Typer | Modern, type-safe CLI |
| VS Code Extension | TypeScript | Required for VS Code |
| AST Parsing | Python `ast` | Built-in, no deps |
| Config | PyYAML | Human-readable |
| Console Output | Rich | Beautiful formatting |
| Testing | pytest | Industry standard |
| Distribution | PyPI + VS Code Marketplace | Standard channels |

---

## 11. PERFORMANCE TARGETS

| Metric | Target | Measurement |
|--------|--------|-------------|
| VS Code Diagnostics | <500ms per file | Time from keystroke to squiggle |
| CLI Scan Speed | <1s per 1000 lines | Batch scanning |
| False Positive Rate | <5% | On automotive test set |
| False Negative Rate | <1% critical | Must not miss SSNs, credit cards |
| Memory Usage | <100MB | For typical 50K line project |

---

## 12. TESTING STRATEGY

### Test Pyramid
- **Unit (70%):** Individual detectors, context analyzer, config loading
- **Integration (20%):** Scanner with real Python files
- **E2E (10%):** Full CLI workflows, VS Code extension

### Key Test Cases

```python
# Test: Email detection
def test_email_detected():
    source = 'email = "user@example.com"'
    violations = scan(source)
    assert len(violations) == 1
    assert violations[0].type == 'email'

# Test: Allowlist respected
def test_email_allowlist():
    config = {'allowlist': ['example.com']}
    source = 'email = "user@example.com"'
    violations = scan(source, config)
    assert len(violations) == 0

# Test: Test file lower severity
def test_test_file_lower_severity():
    violations = scan(source, file_path='tests/test_email.py')
    assert violations[0].severity == Severity.LOW

# Test: LLM API flow elevates severity
def test_llm_flow_critical():
    source = '''
    email = "user@real.com"
    openai.chat.completions.create(messages=[{"content": email}])
    '''
    violations = scan(source)
    assert violations[0].severity == Severity.CRITICAL
```

---

## 13. DEPLOYMENT

### Python Package (PyPI)

```toml
# pyproject.toml
[project]
name = "sentinel-scan"
version = "0.1.0"
dependencies = [
    "typer>=0.9.0",
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.scripts]
sentinel-scan = "sentinel_scan.cli:app"
```

### VS Code Extension

```bash
# Package and publish
vsce package
vsce publish
```

---

## 14. DEVELOPMENT TIMELINE

### Week 0: Validation (MANDATORY)
- [ ] 10 discovery calls
- [ ] Wireframes/mockups
- [ ] Design partner identified
- [ ] Go/no-go decision

### Week 1-2: Core Engine
- [ ] Detection engine with regex + AST
- [ ] PII detectors (email, phone, SSN, address)
- [ ] VIN detector with checksum
- [ ] Context analyzer (test detection, LLM flows)
- [ ] YAML config loading

### Week 3-4: Interfaces
- [ ] VS Code extension with diagnostics
- [ ] CLI tool with scan command
- [ ] False positive management
- [ ] Console + JSON output
- [ ] Pre-commit hook

### Week 5: Polish + Deploy
- [ ] Documentation
- [ ] Design partner deployment
- [ ] Feedback iteration
- [ ] PyPI + VS Code Marketplace publish

---

## 15. FUTURE ENHANCEMENTS (Phase 2+)

| Feature | Phase | Rationale |
|---------|-------|-----------|
| Incremental scanning | 2 | Performance at scale |
| CI/CD integrations | 2 | GitHub Actions, GitLab |
| Web dashboard | 2 | Team visibility |
| ML detection | 2 | Better context understanding |
| Healthcare templates | 2 | Vertical expansion |
| Multi-language | 3 | JavaScript, Java, Go |
| LSP server | 3 | Better IDE support |

---

## 16. SECURITY & PRIVACY

- **Never send detected data externally** - All processing local
- **Truncate matched text in logs** - Show first/last chars only
- **No telemetry in MVP** - No "phone home"
- **Minimal dependencies** - Reduce supply chain risk

---

## APPENDIX A: Complete Directory Structure

```
Regulatory-Scanner/
├── README.md                           # Project overview
├── context/                            # Documentation & planning
│   ├── SENTINEL_SCAN_PROJECT_BRIEF_v2.md
│   ├── SENTINEL_SCAN_TECHNICAL_SPEC_v2.md
│   ├── CLAUDE.md                       # Development rules
│   ├── PLAN.md                         # Development checklist
│   └── memory-bank/                    # Session continuity
│       ├── projectbrief.md             # One-liner about the app
│       ├── techContext.md              # Stack + versions
│       ├── systemPatterns.md           # Architecture approach
│       ├── activeContext.md            # Current work
│       └── progress.md                 # Done vs remaining
│
├── frontend/                           # Landing page (React/Vite)
│   ├── src/
│   ├── package.json
│   └── ...
│
├── sentinel-scan/                      # Core Python package
│   ├── pyproject.toml                  # Package configuration
│   ├── README.md                       # Package documentation
│   ├── sentinel_scan/
│   │   ├── __init__.py                 # Package exports
│   │   ├── cli.py                      # Typer CLI commands
│   │   ├── scanner.py                  # Main scanner orchestrator
│   │   ├── config.py                   # YAML config loading
│   │   ├── models.py                   # Data models (Violation, etc.)
│   │   ├── formatters/
│   │   │   ├── __init__.py
│   │   │   ├── console.py              # Rich console output
│   │   │   ├── json_output.py          # JSON audit format
│   │   │   └── vscode.py               # VS Code JSON format
│   │   ├── detection/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Detector ABC
│   │   │   ├── registry.py             # Detector factory
│   │   │   ├── pii_detector.py         # PII patterns
│   │   │   ├── vin_detector.py         # VIN with checksum
│   │   │   ├── custom_detector.py      # User-defined patterns
│   │   │   └── context_analyzer.py     # AST-based context
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py               # Rule matching logic
│   │   │   ├── allowlist.py            # Allowlist management
│   │   │   └── exclusions.py           # File/path exclusions
│   │   └── templates/
│   │       ├── default.yaml            # Default configuration
│   │       ├── automotive.yaml         # Automotive industry
│   │       └── healthcare.yaml         # Healthcare (Phase 2)
│   │
│   └── tests/
│       ├── conftest.py                 # pytest fixtures
│       ├── unit/
│       │   ├── test_models.py
│       │   ├── test_config.py
│       │   ├── test_pii_detector.py
│       │   ├── test_vin_detector.py
│       │   ├── test_context_analyzer.py
│       │   └── test_scanner.py
│       ├── integration/
│       │   ├── test_cli.py
│       │   └── test_full_scan.py
│       └── fixtures/
│           ├── clean_code.py           # No violations
│           ├── pii_samples.py          # PII test cases
│           ├── vin_samples.py          # VIN test cases
│           └── configs/                # Test configurations
│
└── sentinel-scan-vscode/               # VS Code extension
    ├── package.json                    # Extension manifest
    ├── tsconfig.json                   # TypeScript config
    ├── src/
    │   ├── extension.ts                # Entry point
    │   ├── diagnostics.ts              # Diagnostic provider
    │   ├── scanner.ts                  # Python subprocess
    │   ├── codeActions.ts              # Quick fixes
    │   ├── hover.ts                    # Hover information
    │   └── statusBar.ts                # Status bar item
    ├── python/
    │   └── scan_file.py                # Standalone scanner
    └── test/
        └── suite/
            └── extension.test.ts
```

---

## APPENDIX B: Module Responsibilities

| Module | Single Responsibility |
|--------|----------------------|
| `cli.py` | Parse arguments, invoke scanner, format output |
| `scanner.py` | Orchestrate detection, aggregate results |
| `config.py` | Load, validate, merge YAML configurations |
| `models.py` | Define data structures (Violation, ScanResult) |
| `detection/base.py` | Define Detector interface |
| `detection/registry.py` | Manage detector registration and instantiation |
| `detection/pii_detector.py` | Detect PII patterns (email, phone, SSN) |
| `detection/vin_detector.py` | Detect and validate VINs |
| `detection/context_analyzer.py` | AST parsing, context determination |
| `rules/engine.py` | Apply rules, filter violations |
| `rules/allowlist.py` | Manage global and per-detector allowlists |
| `formatters/console.py` | Rich-formatted console output |
| `formatters/json_output.py` | Structured JSON for audit logs |

---

## APPENDIX C: Related Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| Project Brief | Business context, value prop, GTM | `context/SENTINEL_SCAN_PROJECT_BRIEF_v2.md` |
| Technical Spec | This document | `context/SENTINEL_SCAN_TECHNICAL_SPEC_v2.md` |
| Development Rules | Coding standards, TDD, approved libs | `context/CLAUDE.md` |
| Development Plan | Phased checklist of tasks | `context/PLAN.md` |
| System Patterns | Architecture diagrams, design patterns | `context/memory-bank/systemPatterns.md` |
| Tech Context | Stack versions, environment | `context/memory-bank/techContext.md` |
| Progress Tracker | What's done, what's left | `context/memory-bank/progress.md` |

---

*Last updated: January 4, 2026*
