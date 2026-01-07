/**
 * Diagnostics provider for Sentinel Scan.
 *
 * Manages VS Code diagnostics (squiggles, problems panel) based on
 * violations detected by the Python scanner.
 */

import * as vscode from 'vscode';
import { Scanner, Violation } from './scanner';

export class SentinelDiagnostics implements vscode.Disposable {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private scanner: Scanner;
    private debounceTimers: Map<string, NodeJS.Timeout>;

    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('sentinel-scan');
        this.scanner = new Scanner();
        this.debounceTimers = new Map();
    }

    /**
     * Dispose of resources.
     */
    dispose(): void {
        this.diagnosticCollection.dispose();
        this.debounceTimers.forEach((timer) => clearTimeout(timer));
    }

    /**
     * Schedule a document scan with debouncing.
     */
    scheduleDocumentScan(document: vscode.TextDocument): void {
        const config = vscode.workspace.getConfiguration('sentinel-scan');
        const scanOnType = config.get<boolean>('scanOnType', true);

        if (!scanOnType) {
            return;
        }

        const uri = document.uri.toString();
        const delay = config.get<number>('debounceDelay', 300);

        // Clear existing timer
        const existingTimer = this.debounceTimers.get(uri);
        if (existingTimer) {
            clearTimeout(existingTimer);
        }

        // Set new timer
        const timer = setTimeout(() => {
            this.scanDocument(document);
            this.debounceTimers.delete(uri);
        }, delay);

        this.debounceTimers.set(uri, timer);
    }

    /**
     * Scan a document and update diagnostics.
     */
    async scanDocument(document: vscode.TextDocument): Promise<void> {
        try {
            const violations = await this.scanner.scanContent(
                document.getText(),
                document.uri.fsPath
            );

            const diagnostics = violations.map((v) => this.violationToDiagnostic(v));
            this.diagnosticCollection.set(document.uri, diagnostics);
        } catch (error) {
            console.error('Sentinel Scan error:', error);
            // Don't show error to user for every scan failure
            // Just clear diagnostics for this file
            this.diagnosticCollection.set(document.uri, []);
        }
    }

    /**
     * Clear diagnostics for a document.
     */
    clearDiagnostics(uri: vscode.Uri): void {
        this.diagnosticCollection.delete(uri);
    }

    /**
     * Convert a violation to a VS Code diagnostic.
     */
    private violationToDiagnostic(violation: Violation): vscode.Diagnostic {
        const range = new vscode.Range(
            violation.line_number - 1,
            violation.column_number,
            violation.line_number - 1,
            violation.end_column
        );

        const severity = this.severityToVscode(violation.severity);

        const diagnostic = new vscode.Diagnostic(
            range,
            `${violation.violation_type.toUpperCase()}: ${violation.message}`,
            severity
        );

        diagnostic.source = 'Sentinel Scan';
        diagnostic.code = {
            value: violation.violation_type,
            target: vscode.Uri.parse('https://sentinelscan.io/docs/violations/' + violation.violation_type)
        };

        return diagnostic;
    }

    /**
     * Convert severity string to VS Code DiagnosticSeverity.
     */
    private severityToVscode(severity: string): vscode.DiagnosticSeverity {
        switch (severity.toUpperCase()) {
            case 'CRITICAL':
                return vscode.DiagnosticSeverity.Error;
            case 'HIGH':
                return vscode.DiagnosticSeverity.Warning;
            case 'MEDIUM':
                return vscode.DiagnosticSeverity.Information;
            case 'LOW':
                return vscode.DiagnosticSeverity.Hint;
            default:
                return vscode.DiagnosticSeverity.Warning;
        }
    }
}
