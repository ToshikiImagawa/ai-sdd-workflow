#!/usr/bin/env pwsh
# session-start.ps1
# SessionStart hook script (Windows/PowerShell version)
# Loads .sdd-config.json at session start (generates if not exists) and initializes environment variables

# Get project root
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

# Path to .sdd-config.json
$ConfigFile = Join-Path $ProjectRoot ".sdd-config.json"

# Default values
$DocsRoot = ".sdd"
$RequirementDir = "requirement"
$SpecificationDir = "specification"
$TaskDir = "task"

# Legacy structure detection and migration warning
$LegacyDetected = $false
$LegacyDocsRoot = ""
$LegacyRequirement = ""
$LegacyTask = ""

# Check for legacy structure only if .sdd-config.json doesn't exist
if (-not (Test-Path $ConfigFile)) {
    # Detect legacy docs root (.docs)
    $DocsPath = Join-Path $ProjectRoot ".docs"
    $SddPath = Join-Path $ProjectRoot ".sdd"
    if ((Test-Path $DocsPath) -and -not (Test-Path $SddPath)) {
        $LegacyDetected = $true
        $LegacyDocsRoot = ".docs"
        $DocsRoot = ".docs"
    }

    # Detect legacy requirement directory (requirement-diagram)
    $ReqDiagramPath = Join-Path (Join-Path $ProjectRoot $DocsRoot) "requirement-diagram"
    if (Test-Path $ReqDiagramPath) {
        $LegacyDetected = $true
        $LegacyRequirement = "requirement-diagram"
        $RequirementDir = "requirement-diagram"
    }

    # Detect legacy task directory (review)
    $ReviewPath = Join-Path (Join-Path $ProjectRoot $DocsRoot) "review"
    $TaskPath = Join-Path (Join-Path $ProjectRoot $DocsRoot) "task"
    if ((Test-Path $ReviewPath) -and -not (Test-Path $TaskPath)) {
        $LegacyDetected = $true
        $LegacyTask = "review"
        $TaskDir = "review"
    }

    if ($LegacyDetected) {
        # Auto-generate .sdd-config.json with legacy values
        $Config = @{
            root = $DocsRoot
            directories = @{
                requirement = $RequirementDir
                specification = $SpecificationDir
                task = $TaskDir
            }
        }
        $Config | ConvertTo-Json -Depth 3 | Set-Content $ConfigFile -Encoding UTF8

        Write-Host "[AI-SDD Migration] Legacy directory structure detected." -ForegroundColor Yellow
        Write-Host "" -ForegroundColor Yellow
        Write-Host "Detected legacy structure:" -ForegroundColor Yellow
        if ($LegacyDocsRoot) { Write-Host "  - Root directory: .docs" -ForegroundColor Yellow }
        if ($LegacyRequirement) { Write-Host "  - Requirement: requirement-diagram" -ForegroundColor Yellow }
        if ($LegacyTask) { Write-Host "  - Task log: review" -ForegroundColor Yellow }
        Write-Host "" -ForegroundColor Yellow
        Write-Host ".sdd-config.json auto-generated based on legacy structure." -ForegroundColor Yellow
        Write-Host "To migrate to new structure, run:" -ForegroundColor Yellow
        Write-Host "  /sdd_migrate - Migrate to new structure" -ForegroundColor Yellow
        Write-Host "" -ForegroundColor Yellow
    } else {
        # No legacy structure detected and no .sdd-config.json exists, auto-generate default config
        $Config = @{
            root = ".sdd"
            directories = @{
                requirement = "requirement"
                specification = "specification"
                task = "task"
            }
        }
        $Config | ConvertTo-Json -Depth 3 | Set-Content $ConfigFile -Encoding UTF8
        Write-Host "[AI-SDD] .sdd-config.json auto-generated." -ForegroundColor Green
    }
}

# Load configuration if file exists
if (Test-Path $ConfigFile) {
    try {
        $Config = Get-Content $ConfigFile -Raw | ConvertFrom-Json
        if ($Config.root) { $DocsRoot = $Config.root }
        if ($Config.directories.requirement) { $RequirementDir = $Config.directories.requirement }
        if ($Config.directories.specification) { $SpecificationDir = $Config.directories.specification }
        if ($Config.directories.task) { $TaskDir = $Config.directories.task }
    } catch {
        Write-Host "[AI-SDD] Warning: Failed to parse .sdd-config.json. Using default values." -ForegroundColor Yellow
    }
}

# Environment variable output
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
    # Remove existing SDD_* environment variables (prevent duplicate writes)
    if (Test-Path $env:CLAUDE_ENV_FILE) {
        $Content = Get-Content $env:CLAUDE_ENV_FILE | Where-Object { $_ -notmatch '^export SDD_' }
        $Content | Set-Content $env:CLAUDE_ENV_FILE -Encoding UTF8
    }
    Output-EnvVars | Add-Content $env:CLAUDE_ENV_FILE -Encoding UTF8
} else {
    # If CLAUDE_ENV_FILE is not available, output to stdout
    # Claude Code hooks read stdout and interpret as environment variables
    Output-EnvVars
}

exit 0
