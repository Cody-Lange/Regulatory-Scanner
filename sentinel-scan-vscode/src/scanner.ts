/**
 * Scanner interface for Sentinel Scan.
 *
 * Communicates with the Python scanner via subprocess,
 * passing source code and receiving violations as JSON.
 */

import * as vscode from 'vscode';
import { spawn } from 'child_process';

/**
 * Represents a violation detected by the scanner.
 */
export interface Violation {
    file_path: string;
    line_number: number;
    column_number: number;
    end_column: number;
    detector: string;
    violation_type: string;
    matched_text: string;
    severity: string;
    regulation: string;
    message: string;
    recommendation: string;
    context_info: Record<string, unknown>;
}

/**
 * Result from scanning a file.
 */
export interface ScanResult {
    violations: Violation[];
    files_scanned: number;
    lines_scanned: number;
    scan_duration_ms: number;
    errors: string[];
}

/**
 * Scanner class that communicates with Python backend.
 */
export class Scanner {
    private pythonPath: string;

    constructor() {
        this.pythonPath = this.getPythonPath();
    }

    /**
     * Get the Python interpreter path from settings.
     */
    private getPythonPath(): string {
        const config = vscode.workspace.getConfiguration('sentinel-scan');
        return config.get<string>('pythonPath', 'python');
    }

    /**
     * Scan file content and return violations.
     */
    async scanContent(content: string, filePath: string): Promise<Violation[]> {
        // TODO: Implement actual Python subprocess communication in Phase 3
        // For now, return empty array (no violations)

        // This is a placeholder implementation
        // The real implementation will:
        // 1. Spawn Python subprocess
        // 2. Pass content via stdin
        // 3. Parse JSON output from stdout
        // 4. Return violations

        return [];
    }

    /**
     * Scan a file by path.
     */
    async scanFile(filePath: string): Promise<ScanResult> {
        // TODO: Implement in Phase 3
        return {
            violations: [],
            files_scanned: 1,
            lines_scanned: 0,
            scan_duration_ms: 0,
            errors: []
        };
    }

    /**
     * Check if the Python scanner is available.
     */
    async isAvailable(): Promise<boolean> {
        return new Promise((resolve) => {
            const process = spawn(this.pythonPath, ['-c', 'import sentinel_scan; print("ok")']);

            process.on('close', (code) => {
                resolve(code === 0);
            });

            process.on('error', () => {
                resolve(false);
            });
        });
    }
}
