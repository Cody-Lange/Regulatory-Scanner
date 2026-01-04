# CLAUDE.md - Development Rules for Sentinel Scan MVP

## Project Overview
Sentinel Scan is a developer-native compliance scanning tool for LLM applications.
Target: 5-week MVP delivering VS Code extension + CLI tool for Python code scanning.

---

## Core Development Rules

### 1. Test-Driven Development (TDD)
- **ALWAYS** write tests before implementation
- Minimum 80% code coverage for core modules
- Test pyramid: 70% unit, 20% integration, 10% E2E
- Every detector MUST have tests for:
  - True positive cases (correctly identifies violations)
  - True negative cases (doesn't flag clean code)
  - Edge cases (partial matches, unicode, malformed data)
  - Allowlist/ignore behavior

### 2. Approved Libraries Only
**Python (Core Engine + CLI):**
- `typer>=0.9.0` - CLI framework
- `pyyaml>=6.0` - Configuration parsing
- `rich>=13.0` - Console output formatting
- `pytest>=7.0` - Testing
- `pytest-cov>=4.0` - Coverage reporting
- `mypy>=1.0` - Type checking
- `ruff>=0.1.0` - Linting and formatting

**TypeScript (VS Code Extension):**
- `vscode` - VS Code API (built-in)
- `typescript>=5.0` - Language
- No additional runtime dependencies (keep extension lightweight)

**DO NOT ADD** new dependencies without documenting rationale in PR.

### 3. Code Quality Standards
- **Type hints required** on all Python functions
- **Docstrings required** on all public functions and classes
- **No `Any` types** unless absolutely necessary (document why)
- **Maximum function length:** 50 lines (extract if longer)
- **Maximum file length:** 500 lines (split if longer)
- Run `ruff check` and `mypy` before every commit
- All code must pass CI checks before merge

### 4. Security First
- **NEVER** send detected sensitive data externally
- **ALWAYS** truncate matched text in logs (first 4 + last 4 chars)
- **NO** telemetry or analytics in MVP
- **Minimal dependencies** to reduce supply chain risk
- Validate all external input (file paths, config files)

### 5. Performance Constraints
- VS Code diagnostics: <500ms per file
- CLI scan: <1 second per 1,000 lines of code
- Memory usage: <100MB for 50K line project
- Profile before optimizing - measure, don't guess

### 6. Git Workflow
- Branch naming: `feature/<name>`, `fix/<name>`, `refactor/<name>`
- Commit messages: imperative mood, <72 chars, reference issue
- PR required for all changes (no direct main commits)
- Squash merge to keep history clean

### 7. Documentation Requirements
- README with installation, usage, configuration
- Inline comments for complex logic only
- Type hints serve as documentation
- Update PLAN.md when completing tasks

---

## Architecture Decisions (Do Not Deviate Without Discussion)

### Detection Engine
- **Regex + AST hybrid** - Regex for pattern matching, AST for context
- **Python `ast` module** - No external parsing libraries
- **Single-pass scanning** - Parse file once, run all detectors

### Configuration
- **YAML format** - Human-readable, supports comments
- **Hierarchical config** - Global → Project → File-level
- **Sensible defaults** - Should work with zero config

### VS Code Extension
- **Subprocess model** - Extension spawns Python scanner
- **JSON communication** - Structured violation data
- **Debounced scanning** - 300ms delay after keystroke

### Output Formats
- **Console** - Human-readable with Rich formatting
- **JSON** - Machine-readable for CI/CD integration
- **SARIF** (future) - Standard format for code analysis

---

## Module Ownership

| Module | Responsibility | Key Files |
|--------|----------------|-----------|
| CLI | Command-line interface | `cli.py` |
| Scanner | Orchestrates detection | `scanner.py` |
| Config | Configuration loading | `config.py` |
| Models | Data structures | `models.py` |
| PII Detector | Email, phone, SSN, etc. | `detection/pii_detector.py` |
| VIN Detector | Vehicle IDs with checksum | `detection/vin_detector.py` |
| Context Analyzer | AST-based context | `detection/context_analyzer.py` |
| Rule Engine | Rule loading + matching | `rules/engine.py` |
| VS Code Extension | IDE integration | `sentinel-scan-vscode/` |

---

## Definition of Done

A feature is complete when:
- [ ] Tests written and passing (TDD)
- [ ] Type hints on all functions
- [ ] Docstrings on public API
- [ ] `ruff check` passes
- [ ] `mypy` passes
- [ ] Performance targets met
- [ ] Documentation updated
- [ ] PR reviewed and approved

---

## Common Patterns

### Adding a New Detector
1. Create class inheriting from `Detector` base
2. Implement `scan(source, tree, context) -> List[Violation]`
3. Register in detector registry
4. Add configuration schema
5. Write comprehensive tests
6. Add to industry templates if applicable

### Adding a New PII Pattern
1. Add regex to `PII_PATTERNS` dict
2. Define severity and regulation mapping
3. Add to default config
4. Write true positive and negative tests
5. Consider false positive scenarios

### Handling False Positives
1. Check allowlist first
2. Check inline ignore comments
3. Check file exclusion patterns
4. Log skipped violations for debugging

---

## Error Handling

- **User-facing errors:** Clear message with fix suggestion
- **Internal errors:** Log with context, don't crash scanner
- **Config errors:** Validate early, fail fast with specific message
- **File errors:** Handle gracefully (permissions, encoding, missing)

---

## Logging

- Use Python `logging` module
- Log levels: DEBUG (verbose), INFO (progress), WARNING (issues), ERROR (failures)
- No logging in production by default (opt-in via --verbose)
- Never log actual sensitive data

---

*Last updated: January 4, 2026*
