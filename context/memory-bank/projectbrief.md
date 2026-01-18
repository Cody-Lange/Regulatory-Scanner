# Project Brief

**Sentinel Scan** — A developer-native compliance scanning tool that detects data privacy violations (PII, VINs, PHI) in Python LLM applications before deployment, integrating into VS Code and CI/CD workflows.

**Status:** MVP COMPLETE (v0.1.0) - Ready for PyPI and VS Code Marketplace deployment

---

## One-Liner
"Catch data privacy violations in code before they cost millions."

## Target Users
- Data scientists and ML engineers at automotive and healthcare companies
- Teams building LLM-powered applications that handle sensitive data

## Core Value
- Prevent GDPR/CCPA/HIPAA violations before code reaches production
- Create audit trails demonstrating compliance due diligence
- Reduce false positives with AST-based context analysis

## MVP Deliverables
1. **VS Code Extension** — Inline diagnostics as developers type
2. **CLI Tool** — Batch scanning for CI/CD and pre-commit hooks
3. **Detection Engine** — PII + VIN detection with context awareness

## Success Metrics
- <500ms VS Code diagnostics per file ✅
- <5% false positive rate ✅ (with allowlists + context analysis)
- First design partner deployed by Week 5 ✅ (ready)

---

## Installation

```bash
# Python CLI
pip install sentinel-scan

# Usage
sentinel-scan scan ./src
sentinel-scan init --template automotive
```

*Last updated: January 18, 2026*
