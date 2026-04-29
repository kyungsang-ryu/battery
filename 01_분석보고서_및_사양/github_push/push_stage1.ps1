# Stage 1 KCI1 GitHub Push Script (Code Only — outputs/ excluded)
# Created: 2026-04-29
# Run from any location. Korean paths handled via direct path strings.

$ErrorActionPreference = "Continue"
$RepoRoot = "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data"

function Step($num, $msg) {
    Write-Host ""
    Write-Host "[$num] $msg" -ForegroundColor Cyan
}

function Check($exitCode, $context) {
    if ($exitCode -ne 0) {
        Write-Host "  WARN: $context exited with code $exitCode" -ForegroundColor Yellow
    }
}

# ============================================================
Write-Host "=== Stage 1 KCI1 GitHub Push (Code Only) ===" -ForegroundColor Green
Write-Host "Repo: $RepoRoot"

if (-not (Test-Path $RepoRoot)) {
    Write-Host "ERROR: Repo path not found: $RepoRoot" -ForegroundColor Red
    exit 1
}

Set-Location $RepoRoot

# ============================================================
Step "0/6" "Pre-flight check"
git status
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not a git repo or git not in PATH." -ForegroundColor Red
    exit 1
}

git remote -v
git branch -a

# ============================================================
Step "1/6" "Update .gitignore (UTF-8, no BOM)"
$gitignorePath = Join-Path $RepoRoot ".gitignore"

# Lines to ensure are present (one per line)
$mustHave = @(
    "outputs/",
    "node_modules/",
    "*.mat",
    "*.MAT",
    "01_분석보고서_및_사양/K1_paper_draft/K1_paper_draft.docx",
    "01_분석보고서_및_사양/K1_paper_draft/node_modules/",
    "01_분석보고서_및_사양/K1_paper_draft/package.json",
    "01_분석보고서_및_사양/K1_paper_draft/package-lock.json",
    "02_실험_데이터/",
    "셀 엑셀파일/",
    "모듈엑셀파일/"
)

# Read existing .gitignore as bytes -> string (UTF-8) to avoid encoding mishap
if (Test-Path $gitignorePath) {
    $existingBytes = [System.IO.File]::ReadAllBytes($gitignorePath)
    $existing = [System.Text.Encoding]::UTF8.GetString($existingBytes)
    $existingLines = $existing -split "`r?`n" | Where-Object { $_ -ne "" }
} else {
    $existingLines = @()
}

$linesToAdd = @()
foreach ($line in $mustHave) {
    if ($existingLines -notcontains $line) {
        $linesToAdd += $line
    }
}

if ($linesToAdd.Count -gt 0) {
    Write-Host "  Adding $($linesToAdd.Count) line(s) to .gitignore:" -ForegroundColor Yellow
    foreach ($l in $linesToAdd) { Write-Host "    + $l" }

    $newContent = ($existingLines + "" + "# Stage 1 additions (2026-04-29)" + $linesToAdd) -join "`r`n"
    $newContent += "`r`n"
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($gitignorePath, $newContent, $utf8NoBom)
    Write-Host "  .gitignore updated." -ForegroundColor Green
} else {
    Write-Host "  .gitignore already complete. No changes." -ForegroundColor Green
}

# ============================================================
Step "2/6" "Untrack outputs/ if previously tracked (file kept on disk)"
git rm -r --cached outputs/ 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  outputs/ removed from index." -ForegroundColor Green
} else {
    Write-Host "  outputs/ was not tracked. Skipping." -ForegroundColor Gray
}

# ============================================================
Step "3/6" "Switch to main and stage code + docs"
git checkout main
Check $LASTEXITCODE "git checkout main"

# Stage only code, docs, and updated .gitignore
git add .gitignore
git add 01_분석보고서_및_사양/
git add algo/
git add ui/
git add tests/

Write-Host ""
Write-Host "  --- staged files ---" -ForegroundColor Yellow
git diff --cached --name-status | Select-Object -First 60
Write-Host "  --------------------"

# ============================================================
Step "4/6" "Commit + push main"
git commit -m "Stage1: KCI1 fractional ECM code, UI K1 view, paper draft scaffold"
$commitCode = $LASTEXITCODE
if ($commitCode -ne 0) {
    Write-Host "  No changes to commit on main (or commit failed)." -ForegroundColor Yellow
}

git push origin main
Check $LASTEXITCODE "git push origin main"

# ============================================================
Step "5/6" "Sync KCI1 / KCI2 / SCI1 / SCI2 / SCI3 with main"
foreach ($br in @("KCI1", "KCI2", "SCI1", "SCI2", "SCI3")) {
    Write-Host "  -> $br" -ForegroundColor Cyan
    git checkout $br
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    SKIP: branch $br not found locally." -ForegroundColor Yellow
        continue
    }
    git merge main --no-edit
    git push origin $br
    Check $LASTEXITCODE "git push origin $br"
}

# ============================================================
Step "6/6" "Return to main and summary"
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
