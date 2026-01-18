/**
 * Scanner interface for Sentinel Scan.
 *
 * Communicates with the Python scanner via subprocess,
 * passing source code and receiving violations as JSON.
 */

import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';

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
 * Bridge response from the Python scanner.
 */
interface BridgeResponse {
    violations?: Violation[];
    files_scanned?: number;
    lines_scanned?: number;
    scan_duration_ms?: number;
    errors?: string[];
    error?: string;
    status?: string;
    version?: string;
}

/**
 * Scanner class that communicates with Python backend.
 */
export class Scanner {
    private pythonPath: string;
    private bridgeProcess: ChildProcess | null = null;
    private pendingRequests: Map<number, {
        resolve: (value: BridgeResponse) => void;
        reject: (reason: Error) => void;
    }> = new Map();
    private requestId = 0;
    private outputBuffer = '';

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
     * Start the bridge process if not already running.
     */
    private async ensureBridgeRunning(): Promise<void> {
        if (this.bridgeProcess && !this.bridgeProcess.killed) {
            return;
        }

        return new Promise((resolve, reject) => {
            this.bridgeProcess = spawn(this.pythonPath, ['-m', 'sentinel_scan.cli', 'bridge'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            this.bridgeProcess.stdout?.on('data', (data: Buffer) => {
                this.outputBuffer += data.toString();
                this.processOutputBuffer();
            });

            this.bridgeProcess.stderr?.on('data', (data: Buffer) => {
                console.error('Sentinel Scan stderr:', data.toString());
            });

            this.bridgeProcess.on('close', (code) => {
                console.log(`Sentinel Scan bridge exited with code ${code}`);
                this.bridgeProcess = null;
                // Reject any pending requests
                for (const [, { reject }] of this.pendingRequests) {
                    reject(new Error('Bridge process closed'));
                }
                this.pendingRequests.clear();
            });

            this.bridgeProcess.on('error', (err) => {
                console.error('Sentinel Scan bridge error:', err);
                reject(err);
            });

            // Give it a moment to start
            setTimeout(resolve, 100);
        });
    }

    /**
     * Process the output buffer for complete JSON responses.
     */
    private processOutputBuffer(): void {
        const lines = this.outputBuffer.split('\n');

        // Keep the last incomplete line in the buffer
        this.outputBuffer = lines.pop() || '';

        for (const line of lines) {
            if (!line.trim()) continue;

            try {
                const response = JSON.parse(line) as BridgeResponse;
                // For simplicity, resolve all pending requests with this response
                // In a more complex implementation, we'd track request IDs
                for (const [id, { resolve }] of this.pendingRequests) {
                    resolve(response);
                    this.pendingRequests.delete(id);
                    break; // Only resolve one request per response
                }
            } catch (e) {
                console.error('Failed to parse bridge response:', line, e);
            }
        }
    }

    /**
     * Send a request to the bridge and wait for response.
     */
    private async sendRequest(request: object): Promise<BridgeResponse> {
        await this.ensureBridgeRunning();

        return new Promise((resolve, reject) => {
            const id = ++this.requestId;
            this.pendingRequests.set(id, { resolve, reject });

            const json = JSON.stringify(request) + '\n';
            this.bridgeProcess?.stdin?.write(json);

            // Timeout after 30 seconds
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error('Request timeout'));
                }
            }, 30000);
        });
    }

    /**
     * Scan file content and return violations.
     */
    async scanContent(content: string, filePath: string): Promise<Violation[]> {
        try {
            const response = await this.sendRequest({
                action: 'scan',
                content: content,
                file_path: filePath
            });

            if (response.error) {
                console.error('Scan error:', response.error);
                return [];
            }

            return response.violations || [];
        } catch (e) {
            console.error('Failed to scan content:', e);
            return [];
        }
    }

    /**
     * Scan a file by path.
     */
    async scanFile(filePath: string): Promise<ScanResult> {
        try {
            // Read file content
            const uri = vscode.Uri.file(filePath);
            const content = await vscode.workspace.fs.readFile(uri);
            const text = new TextDecoder().decode(content);

            const response = await this.sendRequest({
                action: 'scan',
                content: text,
                file_path: filePath
            });

            if (response.error) {
                return {
                    violations: [],
                    files_scanned: 0,
                    lines_scanned: 0,
                    scan_duration_ms: 0,
                    errors: [response.error]
                };
            }

            return {
                violations: response.violations || [],
                files_scanned: response.files_scanned || 1,
                lines_scanned: response.lines_scanned || 0,
                scan_duration_ms: response.scan_duration_ms || 0,
                errors: response.errors || []
            };
        } catch (e) {
            return {
                violations: [],
                files_scanned: 0,
                lines_scanned: 0,
                scan_duration_ms: 0,
                errors: [String(e)]
            };
        }
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

    /**
     * Ping the bridge to check if it's responsive.
     */
    async ping(): Promise<{ status: string; version: string } | null> {
        try {
            const response = await this.sendRequest({ action: 'ping' });
            if (response.status === 'ok') {
                return {
                    status: response.status,
                    version: response.version || 'unknown'
                };
            }
            return null;
        } catch {
            return null;
        }
    }

    /**
     * Dispose of the scanner and kill the bridge process.
     */
    dispose(): void {
        if (this.bridgeProcess) {
            this.bridgeProcess.kill();
            this.bridgeProcess = null;
        }
    }
}
