#!/usr/bin/env pwsh
# session-start.ps1
# SessionStart フック用スクリプト（Windows/PowerShell版）
# セッション開始時に .sdd-config.json を読み込み（存在しなければ生成）、環境変数を初期化する

# プロジェクトルートを取得
if ($env:CLAUDE_PROJECT_DIR) {
    $ProjectRoot = $env:CLAUDE_PROJECT_DIR
} else {
    try {
        $ProjectRoot = git rev-parse --show-toplevel 2>$null
        if (-not $ProjectRoot) {
            $ProjectRoot = Get-Location
        }
    } catch {
        $ProjectRoot = Get-Location
    }
}

# .sdd-config.json のパス
$ConfigFile = Join-Path $ProjectRoot ".sdd-config.json"

# デフォルト値
$DocsRoot = ".sdd"
$RequirementDir = "requirement"
$SpecificationDir = "specification"
$TaskDir = "task"

# 旧構成の検出とマイグレーション警告
$LegacyDetected = $false
$LegacyDocsRoot = ""
$LegacyRequirement = ""
$LegacyTask = ""

# .sdd-config.json が存在しない場合のみ旧構成をチェック
if (-not (Test-Path $ConfigFile)) {
    # 旧ルートディレクトリ (.docs) の検出
    $DocsPath = Join-Path $ProjectRoot ".docs"
    $SddPath = Join-Path $ProjectRoot ".sdd"
    if ((Test-Path $DocsPath) -and -not (Test-Path $SddPath)) {
        $LegacyDetected = $true
        $LegacyDocsRoot = ".docs"
        $DocsRoot = ".docs"
    }

    # 旧要求仕様ディレクトリ (requirement-diagram) の検出
    $ReqDiagramPath = Join-Path (Join-Path $ProjectRoot $DocsRoot) "requirement-diagram"
    if (Test-Path $ReqDiagramPath) {
        $LegacyDetected = $true
        $LegacyRequirement = "requirement-diagram"
        $RequirementDir = "requirement-diagram"
    }

    # 旧タスクディレクトリ (review) の検出
    $ReviewPath = Join-Path (Join-Path $ProjectRoot $DocsRoot) "review"
    $TaskPath = Join-Path (Join-Path $ProjectRoot $DocsRoot) "task"
    if ((Test-Path $ReviewPath) -and -not (Test-Path $TaskPath)) {
        $LegacyDetected = $true
        $LegacyTask = "review"
        $TaskDir = "review"
    }

    if ($LegacyDetected) {
        # 旧構成の値で .sdd-config.json を自動生成
        $Config = @{
            root = $DocsRoot
            directories = @{
                requirement = $RequirementDir
                specification = $SpecificationDir
                task = $TaskDir
            }
        }
        $Config | ConvertTo-Json -Depth 3 | Set-Content $ConfigFile -Encoding UTF8

        Write-Host "[AI-SDD Migration] 旧バージョンのディレクトリ構成を検出しました。" -ForegroundColor Yellow
        Write-Host "" -ForegroundColor Yellow
        Write-Host "検出された旧構成:" -ForegroundColor Yellow
        if ($LegacyDocsRoot) { Write-Host "  - ルートディレクトリ: .docs" -ForegroundColor Yellow }
        if ($LegacyRequirement) { Write-Host "  - 要求仕様: requirement-diagram" -ForegroundColor Yellow }
        if ($LegacyTask) { Write-Host "  - タスクログ: review" -ForegroundColor Yellow }
        Write-Host "" -ForegroundColor Yellow
        Write-Host "旧構成に基づいて .sdd-config.json を自動生成しました。" -ForegroundColor Yellow
        Write-Host "新構成に移行する場合は以下のコマンドを実行してください:" -ForegroundColor Yellow
        Write-Host "  /sdd_migrate - 新構成への移行" -ForegroundColor Yellow
        Write-Host "" -ForegroundColor Yellow
    } else {
        # 旧構成が検出されず、.sdd-config.json も存在しない場合、デフォルトの設定ファイルを自動生成
        $Config = @{
            root = ".sdd"
            directories = @{
                requirement = "requirement"
                specification = "specification"
                task = "task"
            }
        }
        $Config | ConvertTo-Json -Depth 3 | Set-Content $ConfigFile -Encoding UTF8
        Write-Host "[AI-SDD] .sdd-config.json を自動生成しました。" -ForegroundColor Green
    }
}

# 設定ファイルが存在する場合は設定値を読み込む
if (Test-Path $ConfigFile) {
    try {
        $Config = Get-Content $ConfigFile -Raw | ConvertFrom-Json
        if ($Config.root) { $DocsRoot = $Config.root }
        if ($Config.directories.requirement) { $RequirementDir = $Config.directories.requirement }
        if ($Config.directories.specification) { $SpecificationDir = $Config.directories.specification }
        if ($Config.directories.task) { $TaskDir = $Config.directories.task }
    } catch {
        Write-Host "[AI-SDD] Warning: .sdd-config.json の解析に失敗しました。デフォルト値を使用します。" -ForegroundColor Yellow
    }
}

# 環境変数の出力
function Output-EnvVars {
    Write-Output "export SDD_ROOT=`"$DocsRoot`""
    Write-Output "export SDD_REQUIREMENT_DIR=`"$RequirementDir`""
    Write-Output "export SDD_SPECIFICATION_DIR=`"$SpecificationDir`""
    Write-Output "export SDD_TASK_DIR=`"$TaskDir`""
    Write-Output "export SDD_REQUIREMENT_PATH=`"$DocsRoot/$RequirementDir`""
    Write-Output "export SDD_SPECIFICATION_PATH=`"$DocsRoot/$SpecificationDir`""
    Write-Output "export SDD_TASK_PATH=`"$DocsRoot/$TaskDir`""
}

if ($env:CLAUDE_ENV_FILE) {
    # 既存のSDD_*環境変数を削除（重複書き込み対策）
    if (Test-Path $env:CLAUDE_ENV_FILE) {
        $Content = Get-Content $env:CLAUDE_ENV_FILE | Where-Object { $_ -notmatch '^export SDD_' }
        $Content | Set-Content $env:CLAUDE_ENV_FILE -Encoding UTF8
    }
    Output-EnvVars | Add-Content $env:CLAUDE_ENV_FILE -Encoding UTF8
} else {
    # CLAUDE_ENV_FILE がない場合、stdout に出力
    # Claude Code のフックは stdout を読み取り、環境変数として解釈する
    Output-EnvVars
}

exit 0
