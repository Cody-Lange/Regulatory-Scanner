"""Command-line interface for Sentinel Scan.

This module provides the CLI commands using Typer:
- scan: Scan files/directories for compliance violations
- init: Initialize a configuration file
- install-hook: Install git pre-commit hook
"""

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from sentinel_scan import __version__
from sentinel_scan.config import Settings, find_config_file, get_default_config, load_config
from sentinel_scan.formatters.console import ConsoleFormatter
from sentinel_scan.formatters.json_output import JSONFormatter
from sentinel_scan.scanner import Scanner, scan_directory, scan_file

app = typer.Typer(
    name="sentinel-scan",
    help="Developer-native compliance scanning for LLM applications.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"sentinel-scan version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """Sentinel Scan - Catch data privacy violations before they cost millions."""
    pass


@app.command()
def scan(
    path: Annotated[
        Path,
        typer.Argument(
            help="File or directory to scan.",
            exists=True,
            resolve_path=True,
        ),
    ],
    format_: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: console, json",
        ),
    ] = "console",
    severity: Annotated[
        str | None,
        typer.Option(
            "--severity",
            "-s",
            help="Minimum severity to report: low, medium, high, critical",
        ),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "-c",
            help="Path to configuration file.",
            exists=True,
            resolve_path=True,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="Enable verbose output.",
        ),
    ] = False,
    recursive: Annotated[
        bool,
        typer.Option(
            "--recursive",
            "-r",
            help="Recursively scan directories.",
        ),
    ] = True,
) -> None:
    """Scan files for compliance violations.

    Examples:
        sentinel-scan scan ./src
        sentinel-scan scan ./src --format json
        sentinel-scan scan ./src --severity high
        sentinel-scan scan ./src --config sentinel_scan.yaml
    """
    # Load configuration
    if config:
        cfg = load_config(config)
    else:
        # Try to find config file in current directory or parents
        found_config = find_config_file(path if path.is_dir() else path.parent)
        cfg = load_config(found_config)

    # Override severity if specified
    if severity:
        cfg.settings = Settings(
            min_severity=severity,
            exit_on_violation=cfg.settings.exit_on_violation,
        )

    if verbose:
        console.print(f"[dim]Config: {config or 'default'}[/dim]")
        console.print(f"[dim]Severity filter: {cfg.settings.min_severity}[/dim]")
        console.print(f"[dim]Scanning: {path}[/dim]")
        console.print()

    # Perform scan
    try:
        if path.is_file():
            result = scan_file(path, cfg)
        else:
            result = scan_directory(path, recursive=recursive, config=cfg)
    except Exception as e:
        console.print(f"[red]Error during scan: {e}[/red]")
        raise typer.Exit(code=2) from e

    # Handle errors
    if result.errors and verbose:
        for error in result.errors:
            console.print(f"[yellow]Warning: {error}[/yellow]")

    # Format output
    if format_.lower() == "json":
        formatter = JSONFormatter()
        print(formatter.format(result))
    else:
        formatter = ConsoleFormatter(console)
        formatter.format(result)

    # Exit code
    if result.has_violations and cfg.settings.exit_on_violation:
        raise typer.Exit(code=1)


@app.command()
def init(
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output path for config file.",
        ),
    ] = Path("sentinel_scan.yaml"),
    template: Annotated[
        str,
        typer.Option(
            "--template",
            "-t",
            help="Configuration template: default, automotive",
        ),
    ] = "default",
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing config file.",
        ),
    ] = False,
) -> None:
    """Initialize a Sentinel Scan configuration file.

    Creates a sentinel_scan.yaml with default settings.

    Examples:
        sentinel-scan init
        sentinel-scan init --output .sentinel.yaml
        sentinel-scan init --template automotive
    """
    # Check if file exists
    if output.exists() and not force:
        console.print(f"[red]Config file already exists: {output}[/red]")
        console.print("Use --force to overwrite.")
        raise typer.Exit(code=1)

    # Find template file
    templates_dir = Path(__file__).parent / "templates"
    template_file = templates_dir / f"{template}.yaml"

    if not template_file.exists():
        console.print(f"[red]Template not found: {template}[/red]")
        available = [f.stem for f in templates_dir.glob("*.yaml")]
        console.print(f"Available templates: {', '.join(available)}")
        raise typer.Exit(code=1)

    # Copy template to output
    try:
        output.write_text(template_file.read_text())
        console.print(f"[green]✓ Created config file: {output}[/green]")
        console.print(f"  Template: {template}")
        console.print("\nEdit the file to customize settings for your project.")
    except Exception as e:
        console.print(f"[red]Error creating config file: {e}[/red]")
        raise typer.Exit(code=2) from e


@app.command(name="install-hook")
def install_hook(
    hook_type: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Hook type: pre-commit, pre-push",
        ),
    ] = "pre-commit",
    git_dir: Annotated[
        Path | None,
        typer.Option(
            "--git-dir",
            help="Path to .git directory.",
        ),
    ] = None,
) -> None:
    """Install a git hook for automatic scanning.

    Installs a git hook that runs sentinel-scan before commits.

    Examples:
        sentinel-scan install-hook
        sentinel-scan install-hook --type pre-push
    """
    # Find .git directory
    if git_dir:
        hooks_dir = git_dir / "hooks"
    else:
        # Look for .git in current directory
        current = Path.cwd()
        while current != current.parent:
            git_path = current / ".git"
            if git_path.is_dir():
                hooks_dir = git_path / "hooks"
                break
            current = current.parent
        else:
            console.print("[red]Not a git repository. Run from within a git repo or specify --git-dir.[/red]")
            raise typer.Exit(code=1)

    # Ensure hooks directory exists
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Create hook script
    hook_path = hooks_dir / hook_type
    hook_content = f"""#!/bin/sh
# Sentinel Scan {hook_type} hook
# Automatically scans staged Python files for compliance violations

echo "Running Sentinel Scan..."

# Get staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\\.py$')

if [ -z "$STAGED_FILES" ]; then
    echo "No Python files staged for commit."
    exit 0
fi

# Run sentinel-scan on staged files
sentinel-scan scan . --severity high

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "Sentinel Scan found compliance violations!"
    echo "Fix the issues above or use 'git commit --no-verify' to skip."
    exit 1
fi

echo "Sentinel Scan passed!"
exit 0
"""

    try:
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)  # Make executable
        console.print(f"[green]✓ Installed {hook_type} hook: {hook_path}[/green]")
        console.print("\nThe hook will automatically scan Python files before each commit.")
    except Exception as e:
        console.print(f"[red]Error installing hook: {e}[/red]")
        raise typer.Exit(code=2) from e


@app.command(name="bridge")
def bridge_mode() -> None:
    """Run in bridge mode for VS Code extension.

    This command reads JSON requests from stdin and writes JSON responses to stdout.
    It's designed to be called from the VS Code extension.

    Protocol:
        Request: {"action": "scan", "content": "...", "file_path": "..."}
        Response: {"violations": [...], "files_scanned": 1, ...}
    """
    import json

    # Run in a loop, reading JSON from stdin
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            action = request.get("action", "scan")

            if action == "scan":
                content = request.get("content", "")
                file_path = request.get("file_path", "stdin.py")

                # Create scanner with default config
                cfg = get_default_config()
                cfg.allowlist = []  # Don't allowlist for real scans
                scanner = Scanner(cfg)

                # Scan the content
                result = scanner.scan_source(content, file_path)

                # Output JSON response
                response = {
                    "violations": [v.to_dict() for v in result.violations],
                    "files_scanned": result.files_scanned,
                    "lines_scanned": result.lines_scanned,
                    "scan_duration_ms": result.scan_duration_ms,
                    "errors": result.errors,
                }
                print(json.dumps(response), flush=True)

            elif action == "ping":
                print(json.dumps({"status": "ok", "version": __version__}), flush=True)

            else:
                print(json.dumps({"error": f"Unknown action: {action}"}), flush=True)

        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)


if __name__ == "__main__":
    app()
