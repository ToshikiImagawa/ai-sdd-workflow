#!/usr/bin/env node
/**
 * session-start.js
 * クロスプラットフォーム対応のSessionStartフックランチャー
 * OSを検出し、適切なスクリプト（bash/powershell）を実行する
 */

const { execSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

// __dirname を使用してパス解決（環境変数に依存しない）
const scriptsDir = __dirname;
const projectDir = process.env.CLAUDE_PROJECT_DIR || path.dirname(scriptsDir);

const platform = os.platform();

try {
  if (platform === 'win32') {
    // Windows: PowerShell script
    const psScript = path.join(scriptsDir, 'powershell', 'session-start.ps1');

    if (!fs.existsSync(psScript)) {
      console.error(`[AI-SDD] PowerShell script not found: ${psScript}`);
      process.exit(1);
    }

    execSync(`powershell -ExecutionPolicy Bypass -File "${psScript}"`, {
      stdio: 'inherit',
      env: { ...process.env, CLAUDE_PROJECT_DIR: projectDir }
    });
  } else {
    // macOS/Linux: Bash script
    const bashScript = path.join(scriptsDir, 'bash', 'session-start.sh');

    if (!fs.existsSync(bashScript)) {
      console.error(`[AI-SDD] Bash script not found: ${bashScript}`);
      process.exit(1);
    }

    execSync(`bash "${bashScript}"`, {
      stdio: 'inherit',
      env: { ...process.env, CLAUDE_PROJECT_DIR: projectDir }
    });
  }
} catch (error) {
  console.error(`[AI-SDD] Error: ${error.message}`);
  process.exit(1);
}
