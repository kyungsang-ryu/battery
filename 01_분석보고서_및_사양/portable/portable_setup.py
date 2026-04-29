#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""portable_setup.py
Copies the current workspace to a portable folder, excluding GB-scale raw data
and binary documents. Robust against Windows PowerShell 5.1 encoding bugs.

Usage:
    python portable_setup.py
    python portable_setup.py --destination "D:\\battery_portable"
    python portable_setup.py --destination "E:\\battery_portable" --include-data core
    python portable_setup.py --include-data all
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE = SCRIPT_DIR.parents[1]
PORTABLE_README = SCRIPT_DIR / "portable_README.md"

# Folders to exclude when copying the workspace (anywhere they appear)
EXCLUDE_DIR_NAMES = {
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
    "node_modules",
    "runs",
    "figures",
}

EXCLUDE_DIR_PREFIXES = (
    ".codex_",
    "pytest-cache-files-",
)

EXCLUDE_DIR_SUFFIXES = (
    ".egg-info",
)

EXCLUDE_FILE_SUFFIXES = {
    ".pptx", ".ppt", ".pdf", ".xlsx", ".xls", ".xlsm",
    ".mat", ".zip", ".rar", ".7z", ".iso",
    ".parquet", ".h5", ".hdf5", ".pt", ".pth", ".onnx",
    ".bin", ".dll", ".exe", ".pyc", ".tmp",
}

EXCLUDE_FILE_NAMES = {
    "Thumbs.db", "desktop.ini",
}

# Core raw data folders (본 논문 5편 작업에 필요한 모든 데이터)
CORE_DATA_REL = [
    Path("셀 엑셀파일"),
    Path("02_실험_데이터") / "pouch_SOH",
    Path("모듈엑셀파일") / "모듈엑셀파일" / "모듈데이터 엑셀파일(2022.01~2023.07)" / "CH1",
]

# All raw data (core + 옛날 데이터)
EXTRA_DATA_REL = [
    Path("02_실험_데이터") / "18650_SOH",
    Path("02_실험_데이터") / "Cell 데이터★★★★★",
    Path("02_실험_데이터") / "최근셀데이터",
    Path("02_실험_데이터") / "모듈내 셀간 전압편차 경향확인(EXCEL)",
    Path("모듈엑셀파일") / "모듈엑셀파일" / "모듈데이터 엑셀파일(2022.01~2023.07)" / "CH2",
    Path("모듈,셀 엑셀파일_by_고병찬,이중선"),
    Path("03_매뉴얼_및_참고자료"),
    Path("99_상관없는_자료_및_기타"),
]


def should_exclude_dir(name: str) -> bool:
    return (
        name in EXCLUDE_DIR_NAMES
        or any(name.startswith(prefix) for prefix in EXCLUDE_DIR_PREFIXES)
        or any(name.endswith(suffix) for suffix in EXCLUDE_DIR_SUFFIXES)
    )


def should_exclude_file(name: str) -> bool:
    if name in EXCLUDE_FILE_NAMES:
        return True
    if name.startswith("~$"):
        return True
    suf = "".join(Path(name).suffixes[-1:]).lower()
    return suf in EXCLUDE_FILE_SUFFIXES


def copy_workspace_filtered(src: Path, dst: Path) -> tuple[int, int]:
    """Walk src, copy all files to dst, applying exclusion rules.
    Returns: (copied_files, skipped_files)
    """
    copied = 0
    skipped = 0
    for root, dirs, files in os.walk(src):
        # Filter dirs in-place so os.walk skips them
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

        rel_root = Path(root).relative_to(src)
        dst_root = dst / rel_root
        dst_root.mkdir(parents=True, exist_ok=True)

        for f in files:
            if should_exclude_file(f):
                skipped += 1
                continue
            srcf = Path(root) / f
            dstf = dst_root / f
            try:
                shutil.copy2(srcf, dstf)
                copied += 1
            except (OSError, PermissionError) as e:
                print(f"  [skip-error] {srcf.relative_to(src)}: {e}", flush=True)
                skipped += 1
    return copied, skipped


def copy_readme_to_root(dst: Path) -> None:
    """Make the setup guide visible at the portable folder root."""
    if PORTABLE_README.exists():
        shutil.copy2(PORTABLE_README, dst / "portable_README.md")
        print("  -> copied portable_README.md to destination root")


def copy_data_folder(src_root: Path, dst_root: Path, rel: Path) -> int:
    """Bulk copy of a raw data folder. Returns size in bytes."""
    src = src_root / rel
    dst = dst_root / rel

    if not src.exists():
        print(f"  [data] skip (not found): {rel}", flush=True)
        return 0

    # Estimate size first
    total_bytes = 0
    for p in src.rglob("*"):
        if p.is_file():
            try:
                total_bytes += p.stat().st_size
            except OSError:
                pass
    size_mb = total_bytes / (1024 * 1024)
    print(f"  [data] copying: {rel} ({size_mb:,.1f} MB)...", flush=True)

    dst.parent.mkdir(parents=True, exist_ok=True)

    # Use robocopy for speed on Windows; Python shutil is slower for big trees
    if sys.platform == "win32":
        # robocopy: /E include subdirs (incl. empty), /R:0 no retry, /W:0 no wait,
        # /NFL no file list, /NDL no dir list, /NP no progress %, /NJH /NJS no header/summary
        # Encoding-safe: pass paths as Python strings (subprocess handles UTF-16 conversion)
        cmd = ["robocopy", str(src), str(dst), "/E", "/R:0", "/W:0",
               "/NFL", "/NDL", "/NP", "/NJH", "/NJS"]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="cp949", errors="replace")
        # robocopy exit code: 0-7 = success-ish, >= 8 = failure
        if result.returncode >= 8:
            print(f"  [data] WARN robocopy exit={result.returncode} for {rel}", flush=True)
            print(result.stdout, flush=True)
            print(result.stderr, flush=True)
    else:
        shutil.copytree(src, dst, dirs_exist_ok=True)

    return total_bytes


def folder_summary(dst: Path) -> None:
    print()
    print("[summary] file count by top-level entry in destination:")
    total_size = 0
    entries = sorted(dst.iterdir(), key=lambda p: p.name)
    for entry in entries:
        if entry.is_dir():
            count = sum(1 for _ in entry.rglob("*") if _.is_file())
            size_mb = sum(f.stat().st_size for f in entry.rglob("*") if f.is_file()) / (1024 * 1024)
            total_size += size_mb
            print(f"  {entry.name:<50s}  {count:>6} files  {size_mb:>8,.1f} MB")
        elif entry.is_file():
            size_mb = entry.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"  {entry.name:<50s}     1 file   {size_mb:>8,.1f} MB")
    print(f"  {'TOTAL':<50s}            {total_size:>8,.1f} MB")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--destination", default=r"D:\battery_portable",
                    help="Where to create the portable folder")
    ap.add_argument("--include-data", choices=["none", "core", "all"],
                    default="none",
                    help=("none = code/docs only (~50MB), "
                          "core = + main raw (1-3GB), "
                          "all = + legacy (5-10GB+)"))
    args = ap.parse_args()

    dst = Path(args.destination)

    print()
    print("=" * 60)
    print("  Portable Workspace Setup (Python)")
    print("=" * 60)
    print(f"  Source:      {SOURCE}")
    print(f"  Destination: {dst}")
    print(f"  IncludeData: {args.include_data}")
    print()

    if not SOURCE.exists():
        print(f"[ERROR] source not found: {SOURCE}")
        return 1

    source_resolved = SOURCE.resolve()
    destination_resolved = dst.resolve()
    try:
        destination_inside_source = (
            destination_resolved == source_resolved
            or destination_resolved.is_relative_to(source_resolved)
        )
    except AttributeError:
        destination_inside_source = (
            destination_resolved == source_resolved
            or source_resolved in destination_resolved.parents
        )
    if destination_inside_source:
        print("[ERROR] destination must be outside the source workspace:")
        print(f"        source:      {source_resolved}")
        print(f"        destination: {destination_resolved}")
        return 1

    dst.mkdir(parents=True, exist_ok=True)

    # 1) workspace files (excluded raw data, big binaries, env folders)
    print("[copy] workspace files (excluding raw data and big binaries)...")
    copied, skipped = copy_workspace_filtered(SOURCE, dst)
    print(f"  -> copied {copied} files, skipped {skipped} files")
    copy_readme_to_root(dst)

    # 2) optional raw data
    if args.include_data != "none":
        print()
        print(f"[copy] raw data ({args.include_data})...")
        targets = list(CORE_DATA_REL)
        if args.include_data == "all":
            targets += EXTRA_DATA_REL
        for rel in targets:
            copy_data_folder(SOURCE, dst, rel)

    # 3) summary
    folder_summary(dst)

    print()
    print("=" * 60)
    print(f"  Done. Read {dst}\\portable_README.md for next steps.")
    print("=" * 60)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
