# PLAN.md - Sentinel Scan MVP Development Checklist

## Overview
5-week development plan for Sentinel Scan MVP.
**Target:** VS Code extension + CLI tool for Python compliance scanning.

---

## Phase 0: Project Setup (Day 1-2)
- [ ] Initialize Python project with `pyproject.toml`
- [ ] Configure development tools (ruff, mypy, pytest)
- [ ] Set up project directory structure
- [ ] Create base test fixtures
- [ ] Initialize VS Code extension project
- [ ] Set up CI/CD pipeline (GitHub Actions)

---

## Phase 1: Core Engine (Week 1-2)

### 1.1 Data Models
- [ ] Define `Severity` enum (LOW, MEDIUM, HIGH, CRITICAL)
- [ ] Define `Violation` dataclass
- [ ] Define `ScanResult` dataclass
- [ ] Define `ScanContext` dataclass
- [ ] Write model tests

### 1.2 Configuration System
- [ ] Define YAML config schema
- [ ] Implement config loader
- [ ] Implement config validation
- [ ] Support hierarchical config (global → project → file)
- [ ] Create default config
- [ ] Write config tests

### 1.3 Base Detection Framework
- [ ] Define `Detector` abstract base class
- [ ] Implement detector registry
- [ ] Create violation aggregator
- [ ] Write framework tests

### 1.4 Context Analyzer (KEY DIFFERENTIATOR)
- [ ] Implement AST parser wrapper
- [ ] Detect test files (path patterns)
- [ ] Detect test functions (name patterns)
- [ ] Identify comments and docstrings
- [ ] Parse inline ignore comments (`# sentinel-scan: ignore`)
- [ ] Detect LLM API call patterns
- [ ] Implement data flow analysis (basic)
- [ ] Write comprehensive context tests

### 1.5 PII Detector
- [ ] Email pattern with validation
- [ ] Phone number patterns (US formats)
- [ ] SSN pattern with validation
- [ ] Address detection (basic)
- [ ] Credit card patterns with Luhn validation
- [ ] Implement allowlist filtering
- [ ] Write PII detection tests

### 1.6 VIN Detector
- [ ] VIN regex pattern (17 chars, no I/O/Q)
- [ ] Checksum validation algorithm
- [ ] Write VIN detection tests

### 1.7 Scanner Orchestrator
- [ ] Implement main scan function
- [ ] Coordinate detectors
- [ ] Apply context analysis
- [ ] Apply severity adjustments
- [ ] Handle file encoding
- [ ] Write scanner integration tests

---

## Phase 2: CLI Tool (Week 3)

### 2.1 CLI Framework
- [ ] Set up Typer app
- [ ] Implement `scan` command
- [ ] Implement `init` command (generate config)
- [ ] Implement `install-hook` command
- [ ] Add `--format` option (console, json)
- [ ] Add `--severity` filter option
- [ ] Add `--config` option
- [ ] Add `--verbose` option

### 2.2 Console Output
- [ ] Rich-formatted violation display
- [ ] Summary statistics
- [ ] Exit codes (0 = clean, 1 = violations, 2 = error)
- [ ] Progress indicator for large scans

### 2.3 JSON Output
- [ ] Structured JSON format
- [ ] Include scan metadata
- [ ] Include all violation details
- [ ] Audit-ready format

### 2.4 Pre-commit Integration
- [ ] Generate pre-commit hook script
- [ ] Install hook command
- [ ] Uninstall hook command
- [ ] Write hook tests

### 2.5 CLI Testing
- [ ] Unit tests for each command
- [ ] Integration tests with real files
- [ ] E2E tests for full workflows

---

## Phase 3: VS Code Extension (Week 3-4)

### 3.1 Extension Setup
- [ ] Initialize VS Code extension project
- [ ] Configure TypeScript
- [ ] Set up extension manifest (package.json)
- [ ] Define activation events

### 3.2 Python Bridge
- [ ] Create standalone scanner script
- [ ] Implement subprocess spawning
- [ ] JSON communication protocol
- [ ] Handle Python path detection
- [ ] Error handling for subprocess

### 3.3 Diagnostics Provider
- [ ] Implement DiagnosticCollection
- [ ] Map violations to VS Code diagnostics
- [ ] Severity to DiagnosticSeverity mapping
- [ ] Debounced document scanning (300ms)
- [ ] File save event handling

### 3.4 Hover Provider
- [ ] Violation details on hover
- [ ] Regulation information
- [ ] Fix recommendations

### 3.5 Code Actions
- [ ] "Add to allowlist" quick fix
- [ ] "Ignore this line" quick fix
- [ ] "Ignore this violation type" quick fix

### 3.6 Status Bar
- [ ] Violation count display
- [ ] Scan status indicator
- [ ] Click to show violations panel

### 3.7 Configuration
- [ ] Extension settings schema
- [ ] Python path configuration
- [ ] Severity filter settings
- [ ] Enable/disable toggle

### 3.8 Extension Testing
- [ ] Unit tests for core logic
- [ ] Integration tests with mock scanner
- [ ] Manual testing checklist

---

## Phase 4: False Positive Management (Week 4) ✅ COMPLETE

### 4.1 Allowlists
- [x] Global allowlist in config
- [x] Per-detector allowlists
- [x] Regex pattern allowlists (supports `regex:` prefix)
- [x] Write allowlist tests (test_allowlist.py + detector tests)

### 4.2 Inline Ignores
- [x] Parse `# sentinel-scan: ignore` comments
- [x] Support specific type ignores
- [x] Support multiple types per line
- [x] Write inline ignore tests

### 4.3 File Exclusions
- [x] Path pattern exclusions
- [x] Glob pattern support
- [x] Default exclusions (tests, venv)
- [x] Write exclusion tests

---

## Phase 5: Industry Templates (Week 4)

### 5.1 Automotive Template
- [ ] VIN detection (critical)
- [ ] Dealer code patterns
- [ ] Service record patterns
- [ ] GDPR/CCPA regulation mapping

### 5.2 Template Infrastructure
- [ ] Template loading mechanism
- [ ] Template inheritance
- [ ] Template documentation

---

## Phase 6: Polish & Documentation (Week 5)

### 6.1 Documentation
- [ ] README.md with quick start
- [ ] Configuration reference
- [ ] Detector documentation
- [ ] VS Code extension README
- [ ] Contributing guide

### 6.2 Distribution
- [ ] PyPI package configuration
- [ ] VS Code Marketplace configuration
- [ ] Installation verification
- [ ] Version management

### 6.3 Final Testing
- [ ] Full E2E test suite
- [ ] Performance benchmarks
- [ ] Memory profiling
- [ ] Security review

### 6.4 Design Partner Deployment
- [ ] Deploy to design partner
- [ ] Gather feedback
- [ ] Critical bug fixes
- [ ] Documentation updates

---

## Quality Gates

### Before Phase 2 (CLI)
- [ ] Core engine tests passing
- [ ] >80% code coverage
- [ ] All detectors implemented

### Before Phase 3 (VS Code)
- [ ] CLI fully functional
- [ ] JSON output validated
- [ ] Performance targets met

### Before Phase 5 (Templates)
- [ ] VS Code extension functional
- [ ] FP management complete
- [ ] Integration tested

### Before Phase 6 (Ship)
- [ ] All P0 features complete
- [ ] <5% false positive rate
- [ ] <500ms VS Code diagnostics
- [ ] Documentation complete

---

## Risk Mitigation Checkpoints

### Week 1 End
- [ ] Core models defined
- [ ] Config system working
- [ ] At least one detector functional

### Week 2 End
- [ ] All detectors implemented
- [ ] Context analyzer working
- [ ] Scanner orchestration complete

### Week 3 End
- [ ] CLI fully functional
- [ ] VS Code extension basics working
- [ ] JSON output complete

### Week 4 End
- [ ] VS Code extension polished
- [ ] FP management complete
- [ ] Templates ready

### Week 5 End
- [ ] Documentation complete
- [ ] Distribution ready
- [ ] Design partner deployed

---

*Last updated: January 4, 2026*
