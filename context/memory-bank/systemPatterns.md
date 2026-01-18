# System Patterns

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SENTINEL SCAN SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────┐                  ┌─────────────────────┐      │
│   │   VS Code Plugin    │                  │     CLI Tool        │      │
│   │   (TypeScript)      │                  │     (Python)        │      │
│   │                     │                  │                     │      │
│   │  ┌───────────────┐  │                  │  ┌───────────────┐  │      │
│   │  │  Diagnostics  │  │                  │  │    Typer      │  │      │
│   │  │   Provider    │  │                  │  │   Commands    │  │      │
│   │  └───────┬───────┘  │                  │  └───────┬───────┘  │      │
│   │          │          │                  │          │          │      │
│   │  ┌───────▼───────┐  │                  │          │          │      │
│   │  │   Scanner     │  │    subprocess    │          │          │      │
│   │  │   Bridge      │──┼──────JSON────────┼──────────┘          │      │
│   │  │ (spawn Python)│  │                  │                     │      │
│   │  └───────────────┘  │                  │                     │      │
│   └─────────────────────┘                  └─────────────────────┘      │
│                                                                          │
│   ════════════════════════════════════════════════════════════════════  │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    DETECTION ENGINE (Python)                     │   │
│   │                                                                  │   │
│   │   ┌──────────────────────────────────────────────────────────┐  │   │
│   │   │                    SCANNER ORCHESTRATOR                   │  │   │
│   │   │         (coordinates detection, applies context)          │  │   │
│   │   └──────────────────────────┬───────────────────────────────┘  │   │
│   │                              │                                   │   │
│   │   ┌──────────────────────────▼───────────────────────────────┐  │   │
│   │   │                   DETECTION LAYER                         │  │   │
│   │   │                                                           │  │   │
│   │   │  ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐  │  │   │
│   │   │  │    PII      │ │    VIN      │ │      Custom        │  │  │   │
│   │   │  │  Detector   │ │  Detector   │ │    Detectors       │  │  │   │
│   │   │  │             │ │             │ │                    │  │  │   │
│   │   │  │ • Email     │ │ • Pattern   │ │ • User-defined     │  │  │   │
│   │   │  │ • Phone     │ │ • Checksum  │ │   regex patterns   │  │  │   │
│   │   │  │ • SSN       │ │             │ │                    │  │  │   │
│   │   │  │ • Address   │ │             │ │                    │  │  │   │
│   │   │  │ • Credit    │ │             │ │                    │  │  │   │
│   │   │  └─────────────┘ └─────────────┘ └────────────────────┘  │  │   │
│   │   └───────────────────────────────────────────────────────────┘  │   │
│   │                              │                                   │   │
│   │   ┌──────────────────────────▼───────────────────────────────┐  │   │
│   │   │                  CONTEXT ANALYZER                         │  │   │
│   │   │              (AST-based intelligence)                     │  │   │
│   │   │                                                           │  │   │
│   │   │  • Test file detection      • Docstring/comment parsing  │  │   │
│   │   │  • Test function detection  • Inline ignore parsing      │  │   │
│   │   │  • LLM API flow detection   • Severity adjustment        │  │   │
│   │   └───────────────────────────────────────────────────────────┘  │   │
│   │                              │                                   │   │
│   │   ┌──────────────────────────▼───────────────────────────────┐  │   │
│   │   │                    RULE ENGINE                            │  │   │
│   │   │                                                           │  │   │
│   │   │  ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐  │  │   │
│   │   │  │    YAML     │ │  Industry   │ │    Allowlists      │  │  │   │
│   │   │  │   Config    │ │  Templates  │ │    & Exclusions    │  │  │   │
│   │   │  └─────────────┘ └─────────────┘ └────────────────────┘  │  │   │
│   │   └───────────────────────────────────────────────────────────┘  │   │
│   │                              │                                   │   │
│   │   ┌──────────────────────────▼───────────────────────────────┐  │   │
│   │   │                   OUTPUT FORMATTERS                       │  │   │
│   │   │                                                           │  │   │
│   │   │  ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐  │  │   │
│   │   │  │   Console   │ │    JSON     │ │   VS Code JSON     │  │  │   │
│   │   │  │   (Rich)    │ │   (Audit)   │ │   (Diagnostics)    │  │  │   │
│   │   │  └─────────────┘ └─────────────┘ └────────────────────┘  │  │   │
│   │   └───────────────────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Design Patterns

### 1. Strategy Pattern (Detectors)
Each detector implements a common interface, allowing easy extension:

```python
class Detector(ABC):
    @abstractmethod
    def scan(self, source: str, tree: ast.AST, context: ContextAnalysis) -> List[Violation]:
        """Scan source code and return violations."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique detector name."""
        pass
```

### 2. Chain of Responsibility (Violation Processing)
Violations flow through a processing pipeline:

```
Raw Match → Allowlist Filter → Context Filter → Severity Adjuster → Output
```

### 3. Factory Pattern (Detector Registry)
Detectors are registered and instantiated via a central registry:

```python
class DetectorRegistry:
    _detectors: Dict[str, Type[Detector]] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(detector_cls: Type[Detector]) -> Type[Detector]:
            cls._detectors[name] = detector_cls
            return detector_cls
        return decorator

    @classmethod
    def create_all(cls, config: Config) -> List[Detector]:
        return [d(config) for d in cls._detectors.values() if config.is_enabled(d)]
```

### 4. Observer Pattern (VS Code Events)
Extension listens to document changes:

```typescript
// Document change → Debounce → Scan → Update diagnostics
workspace.onDidChangeTextDocument(debounce(scanDocument, 300))
workspace.onDidSaveTextDocument(scanDocument)
workspace.onDidOpenTextDocument(scanDocument)
```

### 5. Strategy Pattern (Allowlist Matching)
Allowlist supports multiple pattern matching strategies:

```python
class AllowlistMatcher:
    """Matches text against literal and regex patterns."""

    def set_patterns(self, patterns: list[str]) -> None:
        # Separate patterns by type for optimized matching
        for pattern in patterns:
            if pattern.startswith("regex:"):
                self._regex_patterns.append(compile(pattern[6:]))
            else:
                self._literal_patterns.append(pattern)

    def is_allowlisted(self, text: str) -> bool:
        # Check literals first (faster), then regex
        if any(p in text for p in self._literal_patterns):
            return True
        return any(r.search(text) for r in self._regex_patterns)
```

Pattern types:
- **Literal**: `"example.com"` - substring match
- **Regex**: `"regex:^test_.*@"` - full regex matching

---

## Data Flow

### CLI Scan Flow
```
1. User runs: sentinel-scan scan ./src
2. CLI parses arguments
3. Config loaded (default + project + overrides)
4. File discovery (glob patterns, exclusions)
5. For each file:
   a. Read and parse to AST
   b. Run all enabled detectors
   c. Apply context analysis
   d. Filter by allowlists
   e. Adjust severities
6. Aggregate violations
7. Format output (console/JSON)
8. Exit with appropriate code
```

### VS Code Scan Flow
```
1. User opens/edits Python file
2. Extension debounces (300ms)
3. Spawn Python subprocess with file content
4. Python scanner returns JSON violations
5. Extension maps to VS Code diagnostics
6. Diagnostics displayed (squiggles, hover, panel)
7. User can apply quick fixes
```

---

## Key Interfaces

### Violation Model
```python
@dataclass
class Violation:
    file_path: str
    line_number: int
    column_number: int
    end_column: int
    detector: str           # "pii", "vin", "custom"
    violation_type: str     # "email", "ssn", "vin"
    matched_text: str       # Truncated for security
    severity: Severity
    regulation: str         # "GDPR Article 6"
    message: str            # Human-readable
    recommendation: str     # How to fix
    context_info: Dict      # Test file, LLM flow, etc.
```

### Configuration Model
```python
@dataclass
class Config:
    version: str
    settings: Settings
    allowlist: List[str]
    exclusions: Exclusions
    detectors: DetectorConfigs
```

---

## Error Handling Strategy

### User Errors (Expected)
- Invalid config file → Clear error message with line number
- Missing file → Skip with warning
- Permission denied → Skip with warning

### Internal Errors (Unexpected)
- Parser failure → Log error, skip file, continue scan
- Detector crash → Log error, skip detector, continue
- Memory issues → Graceful degradation, partial results

### Never Crash the Extension
- VS Code extension must catch all errors
- Show user-friendly messages in status bar
- Log details for debugging

---

## Security Patterns

### Sensitive Data Handling
```python
def truncate_match(text: str, max_visible: int = 4) -> str:
    """Show only first and last N characters."""
    if len(text) <= max_visible * 2:
        return "***"
    return f"{text[:max_visible]}...{text[-max_visible:]}"
```

### No External Communication
- All processing happens locally
- No telemetry, analytics, or "phone home"
- Violations never leave the user's machine

### Dependency Minimization
- Use standard library where possible
- Audit all dependencies before adding
- Lock dependency versions
