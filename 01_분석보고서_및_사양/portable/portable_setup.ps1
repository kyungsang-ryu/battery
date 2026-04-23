# portable_setup.ps1
# Copies workspace files (excluding GB-scale raw data) to a portable folder
# so you can carry it on a USB or sync via cloud and continue at home.
#
# Usage (default destination D:\battery_portable):
#   PS> .\portable_setup.ps1
#
# Custom destination (e.g. USB drive E:\):
#   PS> .\portable_setup.ps1 -Destination "E:\battery_portable"
#
# What gets copied:
#   - 01_분석보고서_및_사양\*.md  (사양·전략·킥오프·핸드오프)
#   - algo\**\*.py                (모든 알고리즘 코드)
#   - ui\**\*.py                  (Streamlit UI 코드)
#   - outputs\**                  (작은 산출물만 — csv/json/png/md, raw 데이터·큰 바이너리 제외)
#   - tests\**\*.py
#   - pyproject.toml
#
# What is EXCLUDED (raw data, big files, env folders):
#   - 02_실험_데이터\, 셀 엑셀파일\, 모듈엑셀파일\ 등 raw 데이터 폴더
#   - 01_분석보고서_및_사양\PPt 파일\, 모듈 및 셀 열화분석 정리본★★★★★\, 셀 실험 정리본\
#   - *.pptx, *.pdf, *.xlsx, *.mat, *.zip 등 큰 바이너리
#   - .venv\, __pycache__\, .git\, .pytest_cache\, .codex_pydeps\, .claude\

param(
    [string]$Destination = "D:\battery_portable",

    # Data copy mode:
    #   "none" : 코드·문서·작은 outputs 만 (default, ~50MB)
    #   "core" : + 본 논문 핵심 raw 데이터 3폴더 (셀 엑셀파일, pouch_SOH, 모듈 CH1) — 보통 1~3 GB
    #   "all"  : + 옛날 데이터 (18650_SOH, Cell 데이터★★★★★, 최근셀데이터, 모듈 CH2 등) — 5~10 GB+
    [ValidateSet("none","core","all")]
    [string]$IncludeData = "none"
)

$Source = "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data"

Write-Host ""
Write-Host "==================================================="
Write-Host " Portable Workspace Setup"
Write-Host "==================================================="
Write-Host " Source:      $Source"
Write-Host " Destination: $Destination"
Write-Host " IncludeData: $IncludeData   (none = code/docs only, core = + main raw, all = + legacy)"
Write-Host ""

if (-not (Test-Path $Source)) {
    Write-Host "[ERROR] Source folder not found: $Source"
    exit 1
}

if (-not (Test-Path $Destination)) {
    Write-Host "[mkdir] creating destination: $Destination"
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
} else {
    Write-Host "[note] destination exists — files will be merged/overwritten (no deletes)"
}

# Excluded directory names (robocopy /XD matches by name anywhere)
$excludeDirNames = @(
    "02_실험_데이터",
    "03_매뉴얼_및_참고자료",
    "99_상관없는_자료_및_기타",
    "셀 엑셀파일",
    "모듈엑셀파일",
    "모듈,셀 엑셀파일_by_고병찬,이중선",
    "PPt 파일",
    "모듈 및 셀 열화분석 정리본★★★★★",
    "셀 실험 정리본",
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".codex_pydeps",
    ".claude",
    ".vscode",
    ".idea",
    "runs",
    "figures"
)

# Excluded file types
$excludeFileTypes = @(
    "*.pptx", "*.ppt", "*.pdf", "*.xlsx", "*.xls", "*.xlsm",
    "*.mat", "*.zip", "*.rar", "*.7z", "*.iso",
    "*.parquet", "*.h5", "*.hdf5", "*.pt", "*.pth", "*.onnx",
    "*.bin", "*.dll", "*.exe", "*.pyc",
    "Thumbs.db", "desktop.ini", "~$*", "*.tmp"
)

# Build robocopy arg arrays
$xdArgs = @()
foreach ($d in $excludeDirNames) { $xdArgs += "/XD"; $xdArgs += $d }

$xfArgs = @()
foreach ($f in $excludeFileTypes) { $xfArgs += "/XF"; $xfArgs += $f }

Write-Host "[copy] running robocopy (this may take 1-2 minutes)..."
Write-Host ""

# /E = include subdirs (empty too)
# /R:0 /W:0 = no retries on failure (avoid hangs)
# /NFL /NDL = quiet (no per-file log)
# /TEE = echo to console
& robocopy $Source $Destination /E /R:0 /W:0 /NFL /NDL @xdArgs @xfArgs

# robocopy exit codes: 0-7 = success-ish, >=8 = failure
if ($LASTEXITCODE -ge 8) {
    Write-Host ""
    Write-Host "[ERROR] robocopy reported failures (exit $LASTEXITCODE)"
    exit $LASTEXITCODE
}

# ─── Optional: copy raw data ───
if ($IncludeData -ne "none") {
    Write-Host ""
    Write-Host "==================================================="
    Write-Host " Raw data copy ($IncludeData)"
    Write-Host "==================================================="
    Write-Host ""

    # Folders for "core" mode — 본 논문에 필요한 raw 데이터만
    $coreFolders = @(
        "셀 엑셀파일",
        "02_실험_데이터\pouch_SOH",
        "모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1"
    )

    # Folders for "all" mode — core + 옛날 데이터까지
    $allFolders = $coreFolders + @(
        "02_실험_데이터\18650_SOH",
        "02_실험_데이터\Cell 데이터★★★★★",
        "02_실험_데이터\최근셀데이터",
        "02_실험_데이터\모듈내 셀간 전압편차 경향확인(EXCEL)",
        "모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH2",
        "모듈,셀 엑셀파일_by_고병찬,이중선",
        "03_매뉴얼_및_참고자료",
        "99_상관없는_자료_및_기타"
    )

    $dataFolders = if ($IncludeData -eq "core") { $coreFolders } else { $allFolders }

    foreach ($rel in $dataFolders) {
        $src = Join-Path $Source $rel
        $dst = Join-Path $Destination $rel

        if (-not (Test-Path $src)) {
            Write-Host "[data] skip (not found): $rel"
            continue
        }

        # Estimate source size
        $sizeMB = [math]::Round(((Get-ChildItem -Path $src -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum) / 1MB, 1)
        Write-Host "[data] copying: $rel ($sizeMB MB)..."

        # Make destination parent
        $dstParent = Split-Path $dst -Parent
        if (-not (Test-Path $dstParent)) {
            New-Item -ItemType Directory -Path $dstParent -Force | Out-Null
        }

        # robocopy this folder
        & robocopy $src $dst /E /R:0 /W:0 /NFL /NDL | Out-Null
        if ($LASTEXITCODE -ge 8) {
            Write-Host "[data]   WARN: robocopy returned exit $LASTEXITCODE for $rel"
        }
    }

    Write-Host "[data] raw data copy complete"
}

# Show summary
Write-Host ""
Write-Host "[summary] file count by top-level folder in destination:"
Get-ChildItem -Path $Destination -Directory | ForEach-Object {
    $count = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
    "{0,-40} {1,5} files" -f $_.Name, $count | Write-Host
}
$rootFiles = (Get-ChildItem -Path $Destination -File -ErrorAction SilentlyContinue).Count
"{0,-40} {1,5} files" -f "(root files)", $rootFiles | Write-Host

# Total size
$total = (Get-ChildItem -Path $Destination -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$totalMB = [math]::Round($total / 1MB, 1)

Write-Host ""
Write-Host "==================================================="
Write-Host " Done. Total size: $totalMB MB"
Write-Host " Portable folder: $Destination"
Write-Host "==================================================="
Write-Host ""
Write-Host " Next: read $Destination\portable_README.md"
Write-Host ""
