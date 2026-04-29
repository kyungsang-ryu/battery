# push_all.ps1
# Pushes 5-paper strategy to https://github.com/kyungsang-ryu/battery
# Branches: main + KCI1 + KCI2 + SCI1 + SCI2 + SCI3
#
# IMPORTANT — PowerShell 5.1 + git interaction:
#   Git writes informational messages (e.g. "From https://...") to stderr.
#   PowerShell 5.1 with $ErrorActionPreference=Stop throws on ANY stderr line,
#   even non-error ones. We use Continue + $LASTEXITCODE checks instead.

$ErrorActionPreference = "Continue"

# ---- Config ----
$REPO_URL     = "https://github.com/kyungsang-ryu/battery.git"
$STRATEGY_DIR = $PSScriptRoot
$WORK_DIR     = Join-Path $env:TEMP "battery_repo_push"

$BRANCHES = @("KCI1", "KCI2", "SCI1", "SCI2", "SCI3")

# Helper — run git, treat stderr as info, only check exit code.
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

function Assert-Git {
    param([int]$ExitCode, [string]$Message)
    if ($ExitCode -ne 0) {
        Write-Host ""
        Write-Host "[FAIL] $Message (exit $ExitCode)" -ForegroundColor Red
        Write-Host "       Aborting. See git output above for details."
        exit $ExitCode
    }
}

Write-Host ""
Write-Host "==================================================="
Write-Host " GitHub 5-paper strategy push"
Write-Host "==================================================="
Write-Host " Repo:     $REPO_URL"
Write-Host " Source:   $STRATEGY_DIR"
Write-Host " Work:     $WORK_DIR"
Write-Host " Branches: main, $($BRANCHES -join ', ')"
Write-Host ""

# ---- Clean work dir ----
if (Test-Path $WORK_DIR) {
    Write-Host "[clean] removing existing work dir"
    Remove-Item -Recurse -Force $WORK_DIR
}

# ---- Step 1: Clone ----
Write-Host "[clone] $REPO_URL"
$ec = Invoke-Git clone $REPO_URL $WORK_DIR
Assert-Git $ec "git clone failed"

Set-Location $WORK_DIR
Invoke-Git config user.name  "Kyungsang Ryu" | Out-Null
Invoke-Git config user.email "ksryu3212@gmail.com" | Out-Null

# ---- Detect main branch state ----
$remoteBranches = & git ls-remote --heads origin 2>$null
$hasRemoteMain = $remoteBranches -match "refs/heads/main"

if (-not $hasRemoteMain) {
    Write-Host ""
    Write-Host "[init] origin/main not found, creating empty main"
    Invoke-Git checkout -b main | Out-Null
    "# battery" | Out-File -FilePath "README.md" -Encoding UTF8
    Invoke-Git add README.md | Out-Null
    Invoke-Git commit -m "init" | Out-Null
    $ec = Invoke-Git push -u origin main
    Assert-Git $ec "initial main push failed"
}

# ---- Step 2: Update main branch README ----
Write-Host ""
Write-Host "--- main branch ---"
Invoke-Git checkout main | Out-Null

# Pull is best-effort — skip if it fails (e.g. just initialized)
& git pull origin main 2>&1 | Out-Null

$mainSrc = Join-Path $STRATEGY_DIR "main_README.md"
if (-not (Test-Path $mainSrc)) {
    Write-Host "[main] source not found: $mainSrc — abort"
    exit 1
}
Copy-Item -Path $mainSrc -Destination "README.md" -Force
Invoke-Git add README.md | Out-Null

$status = & git status --porcelain
if ($status) {
    Invoke-Git commit -m "docs(main): add Multi-Paper strategy README (5 papers, KCI 2 + SCI 3)" | Out-Null
    $ec = Invoke-Git push origin main
    if ($ec -eq 0) {
        Write-Host "[main] pushed"
    } else {
        Write-Host "[main] push returned exit $ec — continuing"
    }
} else {
    Write-Host "[main] no change, skip"
}

# ---- Step 3: 5 strategy branches ----
foreach ($b in $BRANCHES) {
    Write-Host ""
    Write-Host "--- branch $b ---"

    Invoke-Git checkout main | Out-Null

    $remoteExists = & git ls-remote --heads origin $b 2>$null
    if ($remoteExists) {
        Write-Host "[$b] remote exists, checkout"
        Invoke-Git checkout -B $b "origin/$b" | Out-Null
    } else {
        Write-Host "[$b] new branch from main"
        Invoke-Git checkout -b $b | Out-Null
    }

    $srcMd = Join-Path $STRATEGY_DIR ("{0}_strategy.md" -f $b)
    if (-not (Test-Path $srcMd)) {
        Write-Host "[$b] source not found: $srcMd — skip"
        continue
    }
    Copy-Item -Path $srcMd -Destination "strategy.md" -Force
    Invoke-Git add strategy.md | Out-Null

    $status = & git status --porcelain
    if ($status) {
        Invoke-Git commit -m "docs($b): add algorithm development strategy" | Out-Null
        $ec = Invoke-Git push -u origin $b
        if ($ec -eq 0) {
            Write-Host "[$b] pushed"
        } else {
            Write-Host "[$b] push returned exit $ec — see above"
        }
    } else {
        Write-Host "[$b] no change, skip"
    }
}

# ---- Done ----
Set-Location $STRATEGY_DIR
Write-Host ""
Write-Host "==================================================="
Write-Host " Done. Verify at https://github.com/kyungsang-ryu/battery"
Write-Host " Local work dir kept at: $WORK_DIR"
Write-Host "==================================================="
