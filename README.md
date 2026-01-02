# Gorilla Gate

Developer-native compliance scanning tool for LLM applications. Catch data privacy violations before they cost millions.

## Project Structure

```
Regulatory-Scanner/
├── frontend/           # Landing page (React + TypeScript + Tailwind)
│   ├── src/
│   ├── package.json
│   └── README.md      # Frontend-specific documentation
└── context/           # Project context files
```

## Getting Started

### Frontend Development

Navigate to the frontend directory and follow the instructions in the [frontend README](./frontend/README.md).

```bash
cd frontend
npm install
npm run dev
```

## About Gorilla Gate

Gorilla Gate is a compliance scanning tool that helps developers detect and prevent data privacy violations in LLM applications. It provides:

- **Real-time scanning** with VS Code extension
- **Pre-commit hooks** to block violations before they reach production
- **Context-aware detection** using AST analysis
- **Regulatory mapping** to GDPR, CCPA, HIPAA, and more
- **Audit trails** for compliance teams

## License

All rights reserved © 2026 Gorilla Gate
