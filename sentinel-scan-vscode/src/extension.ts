/**
 * Sentinel Scan VS Code Extension
 *
 * This extension provides real-time compliance scanning for Python files,
 * detecting PII, VINs, and other sensitive data before it reaches production.
 */

import * as vscode from 'vscode';
import { SentinelDiagnostics } from './diagnostics';
import { StatusBarManager } from './statusBar';

let diagnostics: SentinelDiagnostics;
let statusBar: StatusBarManager;

/**
 * Called when the extension is activated.
 */
export function activate(context: vscode.ExtensionContext): void {
    console.log('Sentinel Scan extension is now active');

    // Initialize components
    diagnostics = new SentinelDiagnostics();
    statusBar = new StatusBarManager();

    // Register commands
    const scanCommand = vscode.commands.registerCommand(
        'sentinel-scan.scan',
        () => scanCurrentFile()
    );

    const scanWorkspaceCommand = vscode.commands.registerCommand(
        'sentinel-scan.scanWorkspace',
        () => scanWorkspace()
    );

    // Register event handlers
    const onDidChangeTextDocument = vscode.workspace.onDidChangeTextDocument(
        (event) => {
            if (shouldScan(event.document)) {
                diagnostics.scheduleDocumentScan(event.document);
            }
        }
    );

    const onDidSaveTextDocument = vscode.workspace.onDidSaveTextDocument(
        (document) => {
            if (shouldScan(document)) {
                diagnostics.scanDocument(document);
            }
        }
    );

    const onDidOpenTextDocument = vscode.workspace.onDidOpenTextDocument(
        (document) => {
            if (shouldScan(document)) {
                diagnostics.scanDocument(document);
            }
        }
    );

    const onDidCloseTextDocument = vscode.workspace.onDidCloseTextDocument(
        (document) => {
            diagnostics.clearDiagnostics(document.uri);
        }
    );

    // Add to subscriptions
    context.subscriptions.push(
        scanCommand,
        scanWorkspaceCommand,
        onDidChangeTextDocument,
        onDidSaveTextDocument,
        onDidOpenTextDocument,
        onDidCloseTextDocument,
        diagnostics,
        statusBar
    );

    // Scan all open Python documents
    vscode.workspace.textDocuments.forEach((document) => {
        if (shouldScan(document)) {
            diagnostics.scanDocument(document);
        }
    });

    statusBar.show();
}

/**
 * Called when the extension is deactivated.
 */
export function deactivate(): void {
    console.log('Sentinel Scan extension is now deactivated');
}

/**
 * Check if a document should be scanned.
 */
function shouldScan(document: vscode.TextDocument): boolean {
    const config = vscode.workspace.getConfiguration('sentinel-scan');

    if (!config.get<boolean>('enable', true)) {
        return false;
    }

    // Only scan Python files for now
    return document.languageId === 'python';
}

/**
 * Scan the currently active file.
 */
async function scanCurrentFile(): Promise<void> {
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        vscode.window.showInformationMessage('No active file to scan');
        return;
    }

    if (!shouldScan(editor.document)) {
        vscode.window.showInformationMessage('Sentinel Scan only supports Python files');
        return;
    }

    await diagnostics.scanDocument(editor.document);
    vscode.window.showInformationMessage('Sentinel Scan complete');
}

/**
 * Scan all Python files in the workspace.
 */
async function scanWorkspace(): Promise<void> {
    const files = await vscode.workspace.findFiles('**/*.py', '**/node_modules/**');

    if (files.length === 0) {
        vscode.window.showInformationMessage('No Python files found in workspace');
        return;
    }

    vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Scanning workspace...',
            cancellable: true
        },
        async (progress, token) => {
            let scanned = 0;

            for (const file of files) {
                if (token.isCancellationRequested) {
                    break;
                }

                const document = await vscode.workspace.openTextDocument(file);
                await diagnostics.scanDocument(document);

                scanned++;
                progress.report({
                    increment: (100 / files.length),
                    message: `${scanned}/${files.length} files`
                });
            }

            vscode.window.showInformationMessage(
                `Sentinel Scan complete: ${scanned} files scanned`
            );
        }
    );
}
