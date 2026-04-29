# push_workspace.ps1
# Push the WORKSPACE (algo/, ui/, outputs/, tests/, pyproject.toml, 01_분석보고서_및_사양/)
# to the main branch of https://github.com/kyungsang-ryu/battery
#
# How it works:
#   1. Initializes git in the workspace folder (one time)
#   2. Adds .gitignore to exclude venv, raw data, caches, etc.
#   3. Pulls the existing main (with strategy README from prior push_all.ps1)
#   4. Commits everything from workspace
#   5. Pushes to origin main
#
# Usage:
#   PS> cd "D:\...\github_push"
#   PS> .\push_workspace.ps1
#
# All comments and console messages in English to avoid PS 5.1 encoding issues.

$ErrorActionPreference = "Continue"

$REPO_URL  = "https://github.com/kyungsang-ryu/battery.git"
# Script lives in: <WORK_ROOT>\01_분석보고서_및_사양\github_push\
# So WORK_ROOT is two levels up (..\..)
$WORK_ROOT = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WORK_ROOT = $WORK_ROOT.Path

function Invoke-Git {
    $output = & git $args 2>&1
    $exit = $LASTEXITCODE
    foreach ($line in $output) {
        if ($line -is [System.Management.Automation.ErrorRecord]) {
            Write-Host "  $($line.ToString())"
        } else {
            Write-Host "  $line"
        }
    }
    return $exit
}

Write-Host ""
Write-Host "==================================================="
Write-Host " Workspace push to GitHub main"
Write-Host "==================================================="
Write-Host " Repo:      $REPO_URL"
Write-Host " Workspace: $WORK_ROOT"
Write-Host ""

Set-Location $WORK_ROOT

# ---- Step 1: git init / sanity check ----
# .git may exist but be corrupt from a prior failed run. Detect via 'git status'.
$needInit = $true
if (Test-Path ".git") {
    & git status > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[init] .git exists and is healthy, reusing"
        $needInit = $false
    } else {
        Write-Host "[init] .git exists but is broken — removing and re-initializing"
        Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue
    }
}
if ($needInit) {
    Write-Host "[init] git init in workspace"
    Invoke-Git init -b main | Out-Null
}

# Always (re)apply config + remote — idempotent
Write-Host "[init] applying config + remote (idempotent)"
& git config user.name  "Kyungsang Ryu" 2>&1 | Out-Null
& git config user.email "ksryu3212@gmail.com" 2>&1 | Out-Null
& git config core.quotepath false 2>&1 | Out-Null
& git remote remove origin 2>&1 | Out-Null   # ignore if not present
& git remote add origin $REPO_URL 2>&1 | Out-Null

# ---- Step 2: write .gitignore (always overwrite to keep updated) ----
# Strategy: aggressive blacklist (folders + binary extensions),
#           then explicit whitelist for files we DO want to push.
Write-Host "[gitignore] writing .gitignore (strict)"
$gitignore = @'
# === Python ===
.venv/
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# === OS ===
Thumbs.db
desktop.ini
~$*
*.tmp

# === Raw data folders (GB-scale, local only) ===
02_실험_데이터/
03_매뉴얼_및_참고자료/
99_상관없는_자료_및_기타/
셀 엑셀파일/
모듈엑셀파일/
모듈,셀 엑셀파일_by_고병찬,이중선/

# === Bulk document folders inside 01_분석보고서_및_사양/ ===
# These contain large .pptx, .pdf, .xlsx — keep local only
01_분석보고서_및_사양/PPt 파일/
01_분석보고서_및_사양/모듈 및 셀 열화분석 정리본★★★★★/
01_분석보고서_및_사양/셀 실험 정리본/

# === Binary file types (anywhere) ===
*.pptx
*.ppt
*.pdf
*.xlsx
*.xls
*.xlsm
*.mat
*.zip
*.rar
*.7z
*.iso
*.parquet
*.h5
*.hdf5
*.pt
*.pth
*.onnx
*.bin
*.dll
*.exe

# === Run outputs (large, regenerable) ===
outputs/runs/
outputs/figures/

# === IDE ===
.vscode/
.idea/

# === Locks ===
.locks/

# === Whitelist (force-include even if matched above) ===
!outputs/ocv_soc/
!outputs/ocv_soc/*.csv
!outputs/ocv_soc/*.png
!outputs/ocv_soc/*.md
!outputs/ecm/
!outputs/ecm/*.json
!outputs/catalog*.csv
!outputs/catalog*.md
!outputs/recon*.md
!outputs/handoff*.md
!outputs/figures/.gitkeep
!outputs/runs/.gitkeep
!.gitkeep
'@
# Use raw UTF-8 bytes to bypass PowerShell 5.1 encoding bugs with Korean path names
$utf8Bytes = [System.Text.Encoding]::UTF8.GetBytes($gitignore)
$gitignorePath = Join-Path (Get-Location).Path ".gitignore"
[System.IO.File]::WriteAllBytes($gitignorePath, $utf8Bytes)

# ---- Step 3: pull existing main ----
Write-Host ""
Write-Host "[pull] fetching origin main"
& git fetch origin main 2>&1 | Out-Null
$hasOriginMain = git ls-remote --heads origin main 2>$null
if ($hasOriginMain) {
    Write-Host "[pull] origin/main exists, merging (allow unrelated)"
    & git pull origin main --allow-unrelated-histories --no-edit 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[pull] merge had issues. If conflicts, resolve manually then re-run."
        Write-Host "       Common: README.md conflict — keep workspace version."
    }
} else {
    Write-Host "[pull] origin/main not found, will create"
}

# ---- Step 4: stage + commit + push ----
Write-Host ""
Write-Host "[add] staging all workspace files (respecting .gitignore)"
Invoke-Git add . | Out-Null

$status = & git status --porcelain
if ($status) {
    $msg = "stage0: workspace snapshot — algo/, ui/, outputs/, pyproject.toml, tests/, docs"
    Write-Host "[commit] $msg"
    Invoke-Git commit -m $msg | Out-Null

    Write-Host "[push] origin main"
    $ec = Invoke-Git push -u origin main
    if ($ec -eq 0) {
        Write-Host ""
        Write-Host "[ok] pushed. Verify at https://github.com/kyungsang-ryu/battery"
    } else {
        Write-Host ""
        Write-Host "[fail] push returned exit $ec — check messages above."
    }
} else {
    Write-Host "[commit] nothing to commit, working tree clean"
}

Set-Location $PSScriptRoot
Write-Host ""
Write-Host "==================================================="
Write-Host " Done."
Write-Host "==================================================="
