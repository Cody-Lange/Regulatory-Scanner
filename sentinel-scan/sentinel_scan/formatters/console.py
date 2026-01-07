"""Console formatter for Sentinel Scan.

This module provides Rich-formatted console output for scan results.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sentinel_scan.models import ScanResult, Severity, Violation


class ConsoleFormatter:
    """Formats scan results for console output using Rich."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the console formatter.

        Args:
            console: Rich Console instance. Creates one if not provided.
        """
        self.console = console or Console()

    def format(self, result: ScanResult) -> None:
        """Format and print scan results to console.

        Args:
            result: Scan results to format
        """
        if not result.has_violations:
            self._print_clean(result)
        else:
            self._print_violations(result)

    def _print_clean(self, result: ScanResult) -> None:
        """Print message when no violations found."""
        self.console.print(
            Panel(
                f"[green]✓ No compliance violations found[/green]\n\n"
                f"Files scanned: {result.files_scanned}\n"
                f"Lines scanned: {result.lines_scanned}",
                title="Sentinel Scan",
                border_style="green",
            )
        )

    def _print_violations(self, result: ScanResult) -> None:
        """Print violations grouped by file."""
        # Header
        self.console.print(
            Panel(
                f"[red]✗ {result.violation_count} compliance violation(s) found[/red]",
                title="Sentinel Scan",
                border_style="red",
            )
        )

        # Group by file
        by_file = result.violations_by_file()

        for file_path, violations in by_file.items():
            self.console.print(f"\n[bold]{file_path}[/bold]")

            for violation in violations:
                self._print_violation(violation)

        # Summary
        self._print_summary(result)

    def _print_violation(self, violation: Violation) -> None:
        """Print a single violation."""
        severity_color = self._severity_color(violation.severity)

        self.console.print(
            f"  Line {violation.line_number}: "
            f"[{severity_color}]{violation.violation_type.upper()}[/{severity_color}] - "
            f"{violation.message}"
        )
        self.console.print(f"    Matched: {violation.matched_text}")
        self.console.print(f"    Regulation: {violation.regulation}")
        self.console.print(f"    [dim]💡 {violation.recommendation}[/dim]")

    def _print_summary(self, result: ScanResult) -> None:
        """Print summary table."""
        self.console.print()

        table = Table(title="Summary")
        table.add_column("Severity", style="bold")
        table.add_column("Count", justify="right")

        summary = result.to_dict()["summary"]
        table.add_row("[red]Critical[/red]", str(summary["critical"]))
        table.add_row("[yellow]High[/yellow]", str(summary["high"]))
        table.add_row("[blue]Medium[/blue]", str(summary["medium"]))
        table.add_row("[dim]Low[/dim]", str(summary["low"]))

        self.console.print(table)
        self.console.print(f"\nScan duration: {result.scan_duration_ms}ms")

    def _severity_color(self, severity: Severity) -> str:
        """Get Rich color for severity level."""
        colors = {
            Severity.CRITICAL: "red bold",
            Severity.HIGH: "yellow",
            Severity.MEDIUM: "blue",
            Severity.LOW: "dim",
        }
        return colors.get(severity, "white")
