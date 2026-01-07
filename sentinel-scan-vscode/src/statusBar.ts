/**
 * Status bar manager for Sentinel Scan.
 *
 * Displays scan status and violation count in the VS Code status bar.
 */

import * as vscode from 'vscode';

export class StatusBarManager implements vscode.Disposable {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );

        this.statusBarItem.command = 'sentinel-scan.scan';
        this.statusBarItem.tooltip = 'Click to scan current file';

        this.updateStatus(0);
    }

    /**
     * Dispose of resources.
     */
    dispose(): void {
        this.statusBarItem.dispose();
    }

    /**
     * Show the status bar item.
     */
    show(): void {
        this.statusBarItem.show();
    }

    /**
     * Hide the status bar item.
     */
    hide(): void {
        this.statusBarItem.hide();
    }

    /**
     * Update the status bar with violation count.
     */
    updateStatus(violationCount: number): void {
        if (violationCount === 0) {
            this.statusBarItem.text = '$(shield) Sentinel: ✓';
            this.statusBarItem.backgroundColor = undefined;
        } else {
            this.statusBarItem.text = `$(shield) Sentinel: ${violationCount} violation${violationCount === 1 ? '' : 's'}`;
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        }
    }

    /**
     * Show scanning in progress.
     */
    showScanning(): void {
        this.statusBarItem.text = '$(sync~spin) Sentinel: Scanning...';
        this.statusBarItem.backgroundColor = undefined;
    }

    /**
     * Show error state.
     */
    showError(): void {
        this.statusBarItem.text = '$(error) Sentinel: Error';
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
}
