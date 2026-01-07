"""Command-line interface for Sentinel Scan.

This module provides the CLI commands using Typer:
- scan: Scan files/directories for compliance violations
- init: Initialize a configuration file
- install-hook: Install git pre-commit hook
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from sentinel_scan import __version__

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
        Optional[bool],
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
        Optional[str],
        typer.Option(
            "--severity",
            "-s",
            help="Minimum severity to report: low, medium, high, critical",
        ),
    ] = None,
    config: Annotated[
        Optional[Path],
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
) -> None:
    """Scan files for compliance violations.

    Examples:
        sentinel-scan scan ./src
        sentinel-scan scan ./src --format json
        sentinel-scan scan ./src --severity high
    """
    # TODO: Implement scanning logic in Phase 1
    console.print(f"[bold blue]Scanning:[/bold blue] {path}")
    console.print(f"  Format: {format_}")
    console.print(f"  Severity filter: {severity or 'all'}")
    console.print(f"  Config: {config or 'default'}")
    console.print(f"  Verbose: {verbose}")
    console.print("\n[yellow]Scanner not yet implemented. Coming in Phase 1.[/yellow]")


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
    """
    # TODO: Implement config generation in Phase 1
    console.print(f"[bold blue]Initializing config:[/bold blue] {output}")
    console.print(f"  Force overwrite: {force}")
    console.print("\n[yellow]Config generation not yet implemented. Coming in Phase 1.[/yellow]")


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
) -> None:
    """Install a git hook for automatic scanning.

    Installs a git hook that runs sentinel-scan before commits.
    """
    # TODO: Implement hook installation in Phase 2
    console.print(f"[bold blue]Installing hook:[/bold blue] {hook_type}")
    console.print("\n[yellow]Hook installation not yet implemented. Coming in Phase 2.[/yellow]")


if __name__ == "__main__":
    app()
