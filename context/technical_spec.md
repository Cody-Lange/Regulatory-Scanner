# GORILLA GATE - TECHNICAL SPECIFICATION
**Version:** 1.0  
**Last Updated:** January 2, 2026  
**Status:** MVP Specification  
**Target Completion:** Week 4, January 2026

---

## TABLE OF CONTENTS
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Detection Engine](#detection-engine)
5. [Rule Engine](#rule-engine)
6. [Integration Layer](#integration-layer)
7. [Data Models](#data-models)
8. [Tech Stack](#tech-stack)
9. [Performance Requirements](#performance-requirements)
10. [Security & Privacy](#security--privacy)
11. [Testing Strategy](#testing-strategy)
12. [Deployment & Distribution](#deployment--distribution)
13. [Future Enhancements](#future-enhancements)

---

## SYSTEM OVERVIEW

### Purpose
Gorilla Gate is a static code analysis tool that scans Python codebases for data privacy compliance violations in LLM applications. It detects sensitive data (PII, PHI, VINs, etc.) being sent to LLM APIs and blocks deployment until violations are resolved.

### Design Principles
1. **Developer-First:** Integrate seamlessly into existing workflows (CLI, Git hooks, IDE)
2. **Fast & Accurate:** <5s scan time for 10K lines, <5% false positive rate
3. **Extensible:** Easy to add new detectors and rules without touching core
4. **Actionable:** Clear error messages with line numbers, violation types, and fix suggestions
5. **Auditable:** Generate compliance reports for regulators and internal teams

### MVP Scope (Phase 1)
**IN SCOPE:**
- ✅ CLI tool for scanning Python files
- ✅ Regex-based PII detection (emails, phones, SSNs, addresses)
- ✅ Automotive-specific detection (VINs)
- ✅ YAML-based rule configuration
- ✅ Console output with violation details
- ✅ Pre-commit Git hook integration
- ✅ JSON export for audit logs

**OUT OF SCOPE (Future Phases):**
- ❌ Web dashboard / UI
- ❌ IDE plugins (VS Code, PyCharm)
- ❌ CI/CD platform integrations (GitHub Actions, GitLab CI)
- ❌ ML-based detection (Phase 2)
- ❌ JavaScript/TypeScript support (Phase 2)
- ❌ Real-time file watching (Phase 2)
- ❌ Team collaboration features (Phase 3)

---

## ARCHITECTURE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      GORILLA GATE CLI                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │   Scanner    │─────▶│  Detection   │─────▶│  Report  │ │
│  │  Orchestrator│      │    Engine    │      │ Generator│ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│         │                      │                    │       │
│         ▼                      ▼                    ▼       │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │    File      │      │     Rule     │      │  Output  │ │
│  │   Parser     │      │    Engine    │      │  Format  │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│         │                      │                    │       │
│         ▼                      ▼                    ▼       │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │     AST      │      │  Detectors   │      │ Console  │ │
│  │   Analysis   │      │  (Regex/ML)  │      │   JSON   │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │  Configuration Layer   │
              │  (YAML rule files)     │
              └────────────────────────┘
```

### Component Interaction Flow

```
1. User runs: `gorilla-gate scan ./src`
2. CLI parses arguments, loads config from gorilla_gate.yaml
3. Scanner orchestrator:
   a. Discovers all Python files in ./src
   b. Parses each file into AST
   c. Passes AST + raw text to Detection Engine
4. Detection Engine:
   a. Loads applicable rules from Rule Engine
   b. Runs each detector (regex, AST-based)
   c. Collects violations with metadata
5. Report Generator:
   a. Formats violations per output format (console/JSON)
   b. Calculates severity, groups by file
   c. Returns exit code (0 = clean, 1 = violations)
6. Output displayed to user
```

---

## CORE COMPONENTS

### 1. CLI Interface (`cli.py`)

**Responsibilities:**
- Parse command-line arguments
- Load configuration files
- Invoke scanner
- Handle errors and exit codes

**Commands:**
```bash
# Scan entire directory
gorilla-gate scan ./src

# Scan specific files
gorilla-gate scan file1.py file2.py

# Scan with custom config
gorilla-gate scan ./src --config custom_rules.yaml

# Output to JSON
gorilla-gate scan ./src --format json --output violations.json

# Install pre-commit hook
gorilla-gate install-hook

# Show version/info
gorilla-gate version
gorilla-gate info
```

**Implementation:**
```python
import click
from gorilla_gate.scanner import Scanner
from gorilla_gate.config import load_config

@click.group()
def cli():
    """Gorilla Gate - Compliance scanning for LLM applications"""
    pass

@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--config', default='gorilla_gate.yaml', help='Config file path')
@click.option('--format', default='console', type=click.Choice(['console', 'json']))
@click.option('--output', default=None, help='Output file for JSON format')
def scan(paths, config, format, output):
    """Scan files for compliance violations"""
    cfg = load_config(config)
    scanner = Scanner(cfg)
    violations = scanner.scan(paths)
    
    if format == 'json':
        write_json(violations, output)
    else:
        print_console(violations)
    
    # Exit with error if violations found
    sys.exit(1 if violations else 0)
```

---

### 2. Scanner Orchestrator (`scanner.py`)

**Responsibilities:**
- Discover files to scan
- Parse files into AST + text
- Coordinate detection across files
- Aggregate results

**Key Methods:**
```python
class Scanner:
    def __init__(self, config: Config):
        self.config = config
        self.detection_engine = DetectionEngine(config)
    
    def scan(self, paths: List[str]) -> List[Violation]:
        """Scan all Python files in given paths"""
        files = self._discover_files(paths)
        violations = []
        
        for file_path in files:
            file_violations = self._scan_file(file_path)
            violations.extend(file_violations)
        
        return violations
    
    def _discover_files(self, paths: List[str]) -> List[str]:
        """Recursively find all .py files"""
        # Handle directories, individual files, .gitignore patterns
        pass
    
    def _scan_file(self, file_path: str) -> List[Violation]:
        """Parse and scan a single file"""
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        # Parse into AST
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            # Log and skip invalid files
            return []
        
        # Run detection
        return self.detection_engine.detect(file_path, source_code, tree)
```

---

### 3. Detection Engine (`detection/engine.py`)

**Responsibilities:**
- Load and manage detectors
- Run detectors against code
- Collect and deduplicate violations

**Architecture:**
```python
class DetectionEngine:
    def __init__(self, config: Config):
        self.detectors = self._load_detectors(config)
    
    def detect(self, file_path: str, source: str, tree: ast.AST) -> List[Violation]:
        """Run all enabled detectors"""
        violations = []
        
        for detector in self.detectors:
            if detector.is_enabled(file_path):
                detected = detector.scan(source, tree)
                violations.extend(detected)
        
        # Deduplicate if same violation detected by multiple detectors
        return self._deduplicate(violations)
    
    def _load_detectors(self, config: Config) -> List[Detector]:
        """Instantiate detectors based on config"""
        detectors = []
        
        if config.detectors.pii.enabled:
            detectors.append(PIIDetector(config.detectors.pii))
        if config.detectors.vin.enabled:
            detectors.append(VINDetector(config.detectors.vin))
        # ... more detectors
        
        return detectors
```

---

## DETECTION ENGINE

### Detector Interface

All detectors implement this base class:

```python
from abc import ABC, abstractmethod
from typing import List
import ast

class Detector(ABC):
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    def scan(self, source: str, tree: ast.AST) -> List[Violation]:
        """Scan source code and return violations"""
        pass
    
    def is_enabled(self, file_path: str) -> bool:
        """Check if detector should run on this file"""
        # Check file patterns, exclusions, etc.
        return True
```

---

### PII Detector (`detection/pii_detector.py`)

**Detects:** Emails, phone numbers, SSNs, addresses, credit cards

**Approach:** Regex patterns against source code text + AST analysis for context

**Implementation:**
```python
import re
from typing import List

class PIIDetector(Detector):
    # Regex patterns for common PII
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    
    def scan(self, source: str, tree: ast.AST) -> List[Violation]:
        violations = []
        
        # Scan for emails
        for match in re.finditer(self.EMAIL_PATTERN, source):
            # Get line number from character position
            line_num = source[:match.start()].count('\n') + 1
            
            # Check if this is in a string literal (not a variable name)
            if self._is_in_string_context(match, tree):
                violations.append(Violation(
                    detector='pii',
                    violation_type='email',
                    line_number=line_num,
                    matched_text=match.group(),
                    severity='high',
                    regulation='GDPR Article 6'
                ))
        
        # Repeat for phone, SSN, etc.
        return violations
    
    def _is_in_string_context(self, match, tree: ast.AST) -> bool:
        """Check if matched text is inside a string literal"""
        # AST traversal to verify this is actual data, not code
        pass
```

---

### VIN Detector (`detection/vin_detector.py`)

**Detects:** Vehicle Identification Numbers (17-character alphanumeric)

**Approach:** Regex + checksum validation

**Implementation:**
```python
class VINDetector(Detector):
    # VIN is 17 characters, no I, O, Q
    VIN_PATTERN = r'\b[A-HJ-NPR-Z0-9]{17}\b'
    
    def scan(self, source: str, tree: ast.AST) -> List[Violation]:
        violations = []
        
        for match in re.finditer(self.VIN_PATTERN, source):
            vin = match.group()
            
            # Validate VIN checksum (basic validation)
            if self._is_valid_vin(vin):
                line_num = source[:match.start()].count('\n') + 1
                violations.append(Violation(
                    detector='vin',
                    violation_type='vin',
                    line_number=line_num,
                    matched_text=vin,
                    severity='critical',
                    regulation='GDPR + Automotive Data Regulations'
                ))
        
        return violations
    
    def _is_valid_vin(self, vin: str) -> bool:
        """Basic VIN validation (checksum, format)"""
        # Implement VIN checksum algorithm
        pass
```

---

### Context-Aware Detection (AST-Based)

**Problem:** Not all detected patterns are violations. Need to understand code context.

**Examples:**
- `"Ford"` the company vs. `"Ford"` a person's name
- Test data vs. production data
- Comments vs. actual code

**Approach:** AST traversal to understand where detected text appears

```python
class ContextAnalyzer:
    @staticmethod
    def get_violation_context(source: str, line_num: int, tree: ast.AST) -> dict:
        """Determine context of a detected violation"""
        # Find the AST node at this line
        node = find_node_at_line(tree, line_num)
        
        return {
            'in_function': get_function_name(node),
            'variable_name': get_variable_name(node),
            'is_test_file': 'test_' in source or '/tests/' in source,
            'is_comment': is_in_comment(source, line_num),
            'is_string_literal': isinstance(node, ast.Str),
            'assigned_to_llm_call': is_passed_to_llm(node, tree)
        }
```

**Key insight:** Focus on violations where data flows to LLM APIs:
```python
# HIGH PRIORITY: Data sent to LLM
customer_email = "user@example.com"
response = openai.chat.completions.create(
    messages=[{"role": "user", "content": f"Email: {customer_email}"}]
)

# MEDIUM PRIORITY: Data in variables (might be sent later)
user_data = {"email": "user@example.com"}

# LOW PRIORITY: Hardcoded test data
TEST_EMAIL = "test@example.com"  # Likely safe

# IGNORE: Comments, docstrings
# Example email: user@example.com
```

---

## RULE ENGINE

### Rule Definition Format (YAML)

**File:** `gorilla_gate.yaml`

```yaml
# Gorilla Gate Configuration
version: "1.0"

# Global settings
settings:
  strictness: "medium"  # low, medium, high
  exit_on_violation: true
  parallel_scanning: true
  max_workers: 4

# Detector configuration
detectors:
  pii:
    enabled: true
    severity: "high"
    patterns:
      email:
        enabled: true
        pattern: '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        severity: "high"
      phone:
        enabled: true
        pattern: '\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        severity: "medium"
      ssn:
        enabled: true
        pattern: '\b\d{3}-\d{2}-\d{4}\b'
        severity: "critical"
    
    # Allowlist (patterns to ignore)
    allowlist:
      - "example.com"  # Test domains
      - "test@"  # Test emails
      - "555-0100"  # Test phone numbers
  
  vin:
    enabled: true
    severity: "critical"
    validate_checksum: true
  
  custom:
    enabled: true
    patterns:
      # Customer-defined sensitive patterns
      - name: "internal_id"
        pattern: 'CUST-\d{6}'
        severity: "medium"
        description: "Internal customer ID format"

# File exclusions
exclusions:
  paths:
    - "*/tests/*"
    - "*/test_*.py"
    - "*/.venv/*"
    - "*/node_modules/*"
  
  patterns:
    - "# gorilla-gate: ignore"  # Inline ignore comment

# Regulatory mapping
regulations:
  gdpr:
    enabled: true
    violations:
      - email
      - phone
      - address
  
  ccpa:
    enabled: true
    violations:
      - email
      - ssn
  
  automotive:
    enabled: true
    violations:
      - vin

# Output settings
output:
  format: "console"  # console, json, sarif
  verbosity: "normal"  # minimal, normal, verbose
  show_context: true  # Show surrounding code lines
  context_lines: 2
```

---

### Rule Loading & Validation

```python
from dataclasses import dataclass
from typing import List, Dict
import yaml

@dataclass
class RuleConfig:
    name: str
    pattern: str
    severity: str
    enabled: bool
    description: str = ""

class Config:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.data = yaml.safe_load(f)
        
        self._validate()
    
    def _validate(self):
        """Validate config structure and values"""
        required_keys = ['version', 'detectors']
        for key in required_keys:
            if key not in self.data:
                raise ValueError(f"Missing required config key: {key}")
    
    @property
    def detectors(self):
        return self.data['detectors']
    
    def get_detector_config(self, detector_name: str) -> dict:
        return self.detectors.get(detector_name, {})
```

---

## INTEGRATION LAYER

### Git Pre-Commit Hook

**Installation:**
```bash
gorilla-gate install-hook
```

**Generated hook file:** `.git/hooks/pre-commit`
```bash
#!/bin/bash
# Gorilla Gate pre-commit hook

# Get list of staged Python files
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$FILES" ]; then
    exit 0
fi

# Run Gorilla Gate scan
gorilla-gate scan $FILES

# Exit with scan result (1 = violations, blocks commit)
exit $?
```

**User experience:**
```bash
$ git commit -m "Add customer analysis"
Running Gorilla Gate compliance scan...

❌ VIOLATIONS FOUND:

File: src/analytics.py
Line 47: Email address detected in LLM prompt
  Matched: "customer@example.com"
  Severity: HIGH
  Regulation: GDPR Article 6
  
  45 | def analyze_sentiment(customer_data):
  46 |     prompt = f"Analyze this customer: {customer_data['email']}"
  47 |     response = openai.chat.completions.create(
  48 |         messages=[{"role": "user", "content": prompt}]
  49 |     )

❌ Commit blocked. Fix violations or use --no-verify to bypass.
```

---

### Python SDK (Future Enhancement)

```python
# For programmatic use
from gorilla_gate import GGScanner

scanner = GGScanner(config_file='custom_rules.yaml')
violations = scanner.scan_file('analytics.py')

if violations:
    for v in violations:
        print(f"{v.file}:{v.line} - {v.violation_type}")
```

---

## DATA MODELS

### Violation Model

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Violation:
    # File context
    file_path: str
    line_number: int
    column_number: Optional[int] = None
    
    # Violation details
    detector: str  # Which detector found this
    violation_type: str  # email, phone, vin, etc.
    matched_text: str  # The actual sensitive data found
    severity: Severity
    
    # Regulatory context
    regulation: str  # GDPR, HIPAA, etc.
    regulation_article: Optional[str] = None
    
    # Code context
    function_name: Optional[str] = None
    variable_name: Optional[str] = None
    surrounding_code: Optional[str] = None
    
    # Recommendations
    recommendation: str = "Remove sensitive data before sending to LLM"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            'file': self.file_path,
            'line': self.line_number,
            'type': self.violation_type,
            'matched': self.matched_text[:20] + '...',  # Truncate for privacy
            'severity': self.severity.value,
            'regulation': self.regulation,
            'recommendation': self.recommendation
        }
```

---

### Scan Result Model

```python
@dataclass
class ScanResult:
    # Summary stats
    files_scanned: int
    lines_scanned: int
    violations_found: int
    violations_by_severity: dict  # {Severity: count}
    
    # Violations
    violations: List[Violation]
    
    # Metadata
    scan_duration_ms: int
    config_file: str
    timestamp: str
    
    def to_json(self) -> str:
        """Export to JSON format"""
        import json
        return json.dumps({
            'summary': {
                'files_scanned': self.files_scanned,
                'lines_scanned': self.lines_scanned,
                'violations_found': self.violations_found,
                'by_severity': {k.value: v for k, v in self.violations_by_severity.items()}
            },
            'violations': [v.to_dict() for v in self.violations],
            'metadata': {
                'duration_ms': self.scan_duration_ms,
                'config': self.config_file,
                'timestamp': self.timestamp
            }
        }, indent=2)
```

---

## TECH STACK

### Core Technologies

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.11+ | Target language for MVP, rich AST support, fast development |
| **CLI Framework** | Click | Simple, powerful, well-documented, decorator-based |
| **Config Format** | YAML (PyYAML) | Human-readable, widely used, supports comments |
| **AST Parsing** | Python `ast` module | Built-in, no dependencies, full Python support |
| **Pattern Matching** | `re` (regex) | Built-in, fast, good enough for MVP |
| **Testing** | pytest | Industry standard, great fixtures, parametrize support |
| **Code Quality** | black, ruff, mypy | Auto-formatting, linting, type checking |
| **Distribution** | PyPI (setuptools) | Standard Python distribution, pip installable |
| **CI/CD** | GitHub Actions | Free for public repos, easy setup |
| **Documentation** | Sphinx + Read the Docs | Professional docs, auto-generated from docstrings |

### Dependencies (Minimal for MVP)

```toml
# pyproject.toml
[project]
name = "gorilla-gate"
version = "0.1.0"
description = "Compliance scanning for LLM applications"
requires-python = ">=3.11"

dependencies = [
    "click>=8.0",
    "pyyaml>=6.0",
    "rich>=13.0",  # For beautiful console output
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
```

---

## PERFORMANCE REQUIREMENTS

### Target Performance

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| **Scan Speed** | <5s for 10K lines | <2s for 10K lines |
| **Memory Usage** | <100MB for typical project | <50MB |
| **Startup Time** | <500ms | <200ms |
| **False Positive Rate** | <5% | <2% |
| **False Negative Rate** | <1% (critical) | <0.1% |

### Optimization Strategies

**For MVP:**
- ✅ Regex-based detection (fast, predictable)
- ✅ Single-pass file scanning
- ✅ Minimal dependencies

**Future optimizations:**
- Parallel file scanning (Python multiprocessing)
- Incremental scanning (only changed files)
- Caching AST parsing results
- Compiled regex patterns
- ML model inference optimization

---

## SECURITY & PRIVACY

### Security Considerations

**Sensitive Data Handling:**
- ❌ **Never send detected sensitive data to external services**
- ✅ Truncate matched text in logs (first 20 chars only)
- ✅ Offer `--redact` flag to completely hide matches
- ✅ Store audit logs locally only (no cloud upload)

**User Privacy:**
- ❌ No telemetry or analytics in MVP
- ❌ No "phone home" behavior
- ✅ All processing happens locally
- ✅ User can audit what data tool accesses (it's just code files)

**Dependencies:**
- Minimal dependency footprint (only trusted, well-maintained packages)
- Regular security updates (Dependabot)
- Supply chain security (verify package hashes)

---

## TESTING STRATEGY

### Test Pyramid

```
         ┌──────────────┐
         │   E2E Tests  │  (10% - Full CLI workflows)
         └──────────────┘
       ┌──────────────────┐
       │ Integration Tests│  (20% - Component interactions)
       └──────────────────┘
    ┌───────────────────────┐
    │     Unit Tests        │  (70% - Individual functions)
    └───────────────────────┘
```

### Unit Tests (`tests/unit/`)

**Coverage target:** 80%+

**Example:**
```python
# tests/unit/test_pii_detector.py
import pytest
from gorilla_gate.detection.pii_detector import PIIDetector

def test_email_detection():
    detector = PIIDetector({})
    source = 'email = "user@example.com"'
    tree = ast.parse(source)
    
    violations = detector.scan(source, tree)
    
    assert len(violations) == 1
    assert violations[0].violation_type == 'email'
    assert violations[0].matched_text == 'user@example.com'

def test_email_allowlist():
    detector = PIIDetector({'allowlist': ['example.com']})
    source = 'email = "user@example.com"'
    tree = ast.parse(source)
    
    violations = detector.scan(source, tree)
    
    assert len(violations) == 0  # Should be ignored

@pytest.mark.parametrize("source,expected_count", [
    ('email = "test@example.com"', 1),
    ('# email: test@example.com', 0),  # Comment, should ignore
    ('TEST_EMAIL = "test@test.com"', 0),  # Test constant
])
def test_context_awareness(source, expected_count):
    detector = PIIDetector({})
    tree = ast.parse(source)
    violations = detector.scan(source, tree)
    assert len(violations) == expected_count
```

### Integration Tests (`tests/integration/`)

**Test full scan workflows:**
```python
# tests/integration/test_scanner.py
def test_full_scan_workflow(tmp_path):
    # Create test files
    test_file = tmp_path / "test.py"
    test_file.write_text('''
        customer_email = "user@example.com"
        openai.chat(prompt=f"Email: {customer_email}")
    ''')
    
    # Create config
    config_file = tmp_path / "gorilla_gate.yaml"
    config_file.write_text('''
        detectors:
          pii:
            enabled: true
    ''')
    
    # Run scanner
    config = load_config(str(config_file))
    scanner = Scanner(config)
    violations = scanner.scan([str(tmp_path)])
    
    assert len(violations) == 1
    assert 'user@example.com' in violations[0].matched_text
```

### End-to-End Tests (`tests/e2e/`)

**Test full CLI:**
```python
# tests/e2e/test_cli.py
from click.testing import CliRunner
from gorilla_gate.cli import cli

def test_cli_scan_violations(tmp_path):
    # Create test project
    test_file = tmp_path / "app.py"
    test_file.write_text('email = "user@example.com"')
    
    # Run CLI
    runner = CliRunner()
    result = runner.invoke(cli, ['scan', str(tmp_path)])
    
    assert result.exit_code == 1  # Violations found
    assert 'email' in result.output
    assert 'GDPR' in result.output
```

### Test Data

**Create realistic test cases:**
```python
# tests/fixtures/sample_violations.py
SAMPLE_CODE_WITH_VIOLATIONS = '''
def analyze_customer(customer_id):
    # Real violation - PII in prompt
    customer_data = db.query(f"SELECT * FROM customers WHERE id = {customer_id}")
    prompt = f"Analyze: {customer_data['email']}, {customer_data['phone']}"
    
    response = openai.chat.completions.create(
        messages=[{"role": "user", "content": prompt}]
    )
    return response

def process_vehicle(vin):
    # Real violation - VIN sent to LLM
    analysis = llm.complete(f"Lookup VIN: {vin}")
    return analysis
'''

SAMPLE_CODE_SAFE = '''
def analyze_customer(customer_id):
    # Safe - PII removed before sending
    customer_data = db.query(f"SELECT * FROM customers WHERE id = {customer_id}")
    anonymized = {
        "age": customer_data['age'],
        "region": customer_data['region'][:2]  # Only state, not full address