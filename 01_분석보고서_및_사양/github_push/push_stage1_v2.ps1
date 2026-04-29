# Stage 1 KCI1 GitHub Push v2 (ASCII-only, encoding-safe)
# Created: 2026-04-29
# Works on Windows PowerShell 5.1 and PowerShell 7+
# No Korean strings inside this file. Repo path is derived from script location.

$ErrorActionPreference = "Continue"

# Derive repo root from this script's location
# This file lives at: <RepoRoot>\01_<korean>\github_push\push_stage1_v2.ps1
# So go up two levels.
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "=== Stage 1 KCI1 GitHub Push (v2 ASCII-safe) ===" -ForegroundColor Green
Write-Host "Repo: $RepoRoot"

if (-not (Test-Path $RepoRoot)) {
    Write-Host "ERROR: Repo path not found: $RepoRoot" -ForegroundColor Red
    exit 1
}

Set-Location -LiteralPath $RepoRoot

# --- 0/6 Sanity check -----------------------------------------------------
Write-Host ""
Write-Host "[0/6] Sanity check" -ForegroundColor Cyan
git status
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not a git repo or git missing." -ForegroundColor Red
    exit 1
}
git remote -v
git branch -a

# --- 1/6 Append new lines to .gitignore (ASCII only) ----------------------
Write-Host ""
Write-Host "[1/6] Append new ASCII lines to .gitignore" -ForegroundColor Cyan
$gitignorePath = Join-Path $RepoRoot ".gitignore"

# Only ASCII rules added here. Korean folder rules from Stage 0 are kept untouched.
$asciiRules = @(
    "outputs/",
    "node_modules/"
)

$existingLines = @()
if (Test-Path $gitignorePath) {
    $bytes = [System.IO.File]::ReadAllBytes($gitignorePath)
    $existingText = [System.Text.Encoding]::UTF8.GetString($bytes)
    $existingLines = $existingText -split "`r?`n"
}

$newLines = @()
foreach ($r in $asciiRules) {
    if ($existingLines -notcontains $r) {
        $newLines += $r
    }
}

if ($newLines.Count -gt 0) {
    Write-Host "  Adding:" -ForegroundColor Yellow
    foreach ($n in $newLines) { Write-Host "    + $n" }
    $appendChunk = "`r`n# Stage 1 additions (2026-04-29)`r`n" + ($newLines -join "`r`n") + "`r`n"
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::AppendAllText($gitignorePath, $appendChunk, $utf8NoBom)
    Write-Host "  .gitignore updated." -ForegroundColor Green
} else {
    Write-Host "  Already up to date." -ForegroundColor Green
}

# --- 2/6 Untrack outputs/ if previously tracked ---------------------------
Write-Host ""
Write-Host "[2/6] Untrack outputs/ (file kept on disk)" -ForegroundColor Cyan
git rm -r --cached outputs/ 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  outputs/ removed from index." -ForegroundColor Green
} else {
    Write-Host "  outputs/ was not tracked. Skipping." -ForegroundColor Gray
}

# --- 3/6 Switch to main and stage everything ------------------------------
Write-Host ""
Write-Host "[3/6] Switch to main and stage all changes" -ForegroundColor Cyan
git checkout main
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: checkout main failed." -ForegroundColor Red
    exit 1
}

# git add -A stages every change (respecting .gitignore).
# This avoids needing to type Korean folder names in PowerShell.
git add -A

Write-Host ""
Write-Host "  --- staged files (first 60) ---" -ForegroundColor Yellow
git diff --cached --name-status | Select-Object -First 60
Write-Host "  --------------------------------"

# Quick sanity: outputs/ must not be in the staged list
$staged = git diff --cached --name-only
$outputsStaged = $staged | Where-Object { $_ -like "outputs/*" }
if ($outputsStaged) {
    Write-Host "  WARNING: outputs/ files are still staged. Aborting before commit." -ForegroundColor Red
    Write-Host $outputsStaged
    exit 1
} else {
    Write-Host "  Verified: no outputs/ files in staging area." -ForegroundColor Green
}

# --- 4/6 Commit and push main --------------------------------------------
Write-Host ""
Write-Host "[4/6] Commit and push main" -ForegroundColor Cyan
git commit -m "Stage1: KCI1 fractional ECM code, UI K1 view, paper draft scaffold"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  No changes to commit on main (or commit failed)." -ForegroundColor Yellow
}
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARN: push origin main returned non-zero." -ForegroundColor Yellow
}

# --- 5/6 Sync the other 5 branches with main -----------------------------
Write-Host ""
Write-Host "[5/6] Sync KCI1, KCI2, SCI1, SCI2, SCI3 with main" -ForegroundColor Cyan
foreach ($br in @("KCI1", "KCI2", "SCI1", "SCI2", "SCI3")) {
    Write-Host ""
    Write-Host "  -> $br" -ForegroundColor Cyan
    git checkout $br
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    SKIP: branch $br not found locally." -ForegroundColor Yellow
        continue
    }
    git merge main --no-edit
    git push origin $br
}

# --- 6/6 Summary ---------------------------------------------------------
Write-Host ""
Write-Host "[6/6] Return to main and summary" -ForegroundColor Cyan
git checkout main
Write-Host ""
Write-Host "Latest commits on main:" -ForegroundColor Yellow
git log --oneline -5
Write-Host ""
Write-Host "All branches:" -ForegroundColor Yellow
git branch -a

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Verify at: https://github.com/kyungsang-ryu/battery"
