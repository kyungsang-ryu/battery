"""KIER dataset catalog and loader helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

from algo.data_io import read_cycler_file

KIER_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = {
    "main_cell": KIER_ROOT / "셀 엑셀파일" / "셀 엑셀파일",
    "pouch_soh": KIER_ROOT / "02_실험_데이터" / "pouch_SOH",
    "module": KIER_ROOT / "모듈엑셀파일" / "모듈엑셀파일" / "모듈데이터 엑셀파일(2022.01~2023.07)" / "CH1",
}

_MAIN_RE = re.compile(
    r"^(?P<date>\d{2}_\d{2}_\d{2})_에기연 열화셀_"
    r"(?P<temp>\d+)deg"
    r"(?:_(?P<cycle>\d+)(?:cycle|Cycle))?"
    r"(?:_(?P<name>RPT|ACIR|DCIR후 충전|DCIR 후 충전|DCIR후충전|DCIR))?"
    r"_(?P<channel>ch\d+)_M01Ch\d+\(\d+\)\.csv$"
)
_POUCH_RE = re.compile(
    r"^(?P<prefix>MG|PVSmoothing|PowerQuality)"
    r"(?:_(?P<temp>\d+)도)?"
    r"_(?P<date>\d{6})"
    r"_(?P<label>MG|PVSmoothing|PowerQuality)"
    r"_(?P<weeks>\d+)"
    r"_(?P<channel>ch\d+)_M01Ch\d+\(\d+\)\.csv$"
)
_MODULE_FILE_RE = re.compile(
    r"^(?P<date>\d{4}_\d{2}_\d{2})_에기연_열화모듈_CYCLE_"
    r"(?P<temp>\d+)deg_(?P<cycle>\d+)cycle"
    r"(?:_(?P<name>RPT|ACIR|DCIR 후 용량충전|DCIR))?"
    r"_(?P<channel>CH\d+)"
    r"(?:\((?P<chunk>\d+)\))?\.csv$"
)
_MODULE_DIR_RE = re.compile(r"^(?P<date>\d{4}_\d{2}_\d{2})_(?P<temp>\d+)deg_(?P<cycle>\d+)cycle$")
_PATTERN_DIR_NAMES = {"Pattern"}
_CATALOG_COLUMNS = [
    "dataset",
    "channel",
    "temp_C",
    "cycle",
    "weeks",
    "type",
    "date",
    "file_path",
    "pattern_chunks",
]


def _normalize_type(name: str | None, parent_name: str) -> str:
    if name:
        compact = name.replace(" ", "")
        if compact == "DCIR후충전":
            return "DCIR후충전"
        return compact
    if parent_name in _PATTERN_DIR_NAMES:
        return "Pattern"
    return parent_name


def _normalize_main_type(name: str | None, parent_name: str) -> str:
    if name:
        return _normalize_type(name, parent_name)
    if parent_name in {"RPT", "DCIR", "ACIR", "Pattern"}:
        return parent_name
    return "Pattern"


def _date_yy_to_iso(text: str) -> str:
    return f"20{text[:2]}-{text[3:5]}-{text[6:8]}"


def _date_yymmdd_to_iso(text: str) -> str:
    return f"20{text[:2]}-{text[2:4]}-{text[4:6]}"


def _date_yyyy_to_iso(text: str) -> str:
    year, month, day = text.split("_")
    return f"{year}-{month}-{day}"


def _empty_row(dataset: str) -> dict:
    return {
        "dataset": dataset,
        "channel": pd.NA,
        "temp_C": pd.NA,
        "cycle": pd.NA,
        "weeks": pd.NA,
        "type": pd.NA,
        "date": pd.NA,
        "file_path": pd.NA,
        "pattern_chunks": None,
    }


def _parse_main_cell_file(path: Path) -> dict | None:
    match = _MAIN_RE.match(path.name)
    if not match:
        return None
    row = _empty_row("main_cell")
    row.update(
        {
            "channel": match.group("channel"),
            "temp_C": int(match.group("temp")),
            "cycle": int(match.group("cycle") or 0),
            "type": _normalize_main_type(match.group("name"), path.parent.name),
            "date": _date_yy_to_iso(match.group("date")),
            "file_path": str(path.resolve()),
        }
    )
    return row


def _parse_pouch_file(path: Path) -> dict | None:
    if any(part.lower().endswith("step") or part.lower() == "step" for part in path.parts):
        return None
    match = _POUCH_RE.match(path.name)
    if not match:
        return None
    folder_temp = re.search(r"(\d+)도", path.parent.name)
    temp_c = int(match.group("temp") or (folder_temp.group(1) if folder_temp else 0))
    pattern_label = match.group("label")
    row = _empty_row("pouch_soh")
    row.update(
        {
            "channel": match.group("channel"),
            "temp_C": temp_c,
            "weeks": int(match.group("weeks")),
            "type": f"Pattern_{pattern_label}",
            "date": _date_yymmdd_to_iso(match.group("date")),
            "file_path": str(path.resolve()),
        }
    )
    return row


def _module_chunk_key(path: Path) -> tuple[int, int]:
    match = _MODULE_FILE_RE.match(path.name)
    if not match:
        return (999999, 999999)
    chunk = match.group("chunk")
    if chunk is None:
        return (0, 0)
    return (1, int(chunk))


def _collect_module_pattern_rows(root: Path) -> list[dict]:
    rows: list[dict] = []
    module_root = root if root.name.upper() == "CH1" else root / "CH1"
    pattern_root = module_root / "Pattern"
    if not pattern_root.exists():
        return rows

    for cycle_dir in sorted(item for item in pattern_root.iterdir() if item.is_dir()):
        dir_match = _MODULE_DIR_RE.match(cycle_dir.name)
        if not dir_match:
            continue

        files = sorted(cycle_dir.glob("*.csv"), key=_module_chunk_key)
        base_files = [path for path in files if "(" not in path.stem]
        if not base_files:
            continue
        base_path = base_files[0]
        chunk_paths = [path.resolve() for path in files]
        file_match = _MODULE_FILE_RE.match(base_path.name)
        if not file_match:
            continue

        row = _empty_row("module")
        row.update(
            {
                "channel": file_match.group("channel"),
                "temp_C": int(dir_match.group("temp")),
                "cycle": int(dir_match.group("cycle")),
                "type": "Pattern",
                "date": _date_yyyy_to_iso(dir_match.group("date")),
                "file_path": str(base_path.resolve()),
                "pattern_chunks": chunk_paths,
            }
        )
        rows.append(row)
    return rows


def _parse_module_file(path: Path) -> dict | None:
    if "Pattern" in path.parts:
        return None
    match = _MODULE_FILE_RE.match(path.name)
    if not match or match.group("chunk") is not None:
        return None
    row = _empty_row("module")
    row.update(
        {
            "channel": match.group("channel"),
            "temp_C": int(match.group("temp")),
            "cycle": int(match.group("cycle")),
            "type": _normalize_type(match.group("name"), path.parent.name),
            "date": _date_yyyy_to_iso(match.group("date")),
            "file_path": str(path.resolve()),
        }
    )
    return row


def _iter_main_rows(root: Path) -> Iterable[dict]:
    for path in root.rglob("*.csv"):
        row = _parse_main_cell_file(path)
        if row is not None:
            yield row


def _iter_pouch_rows(root: Path) -> Iterable[dict]:
    for path in root.rglob("*.csv"):
        row = _parse_pouch_file(path)
        if row is not None:
            yield row


def _iter_module_rows(root: Path) -> Iterable[dict]:
    module_root = root if root.name.upper() == "CH1" else root / "CH1"
    yield from _collect_module_pattern_rows(root)
    for path in module_root.rglob("*.csv"):
        row = _parse_module_file(path)
        if row is not None:
            yield row


def list_kier_files(roots: dict | None = None) -> pd.DataFrame:
    """Return a standard catalog of main cell, pouch SOH, and module runs."""
    roots = roots or SCAN_ROOTS
    rows: list[dict] = []
    for dataset, root_value in roots.items():
        root = Path(root_value)
        if not root.exists():
            continue
        if dataset == "main_cell":
            rows.extend(_iter_main_rows(root))
        elif dataset == "pouch_soh":
            rows.extend(_iter_pouch_rows(root))
        elif dataset == "module":
            rows.extend(_iter_module_rows(root))

    catalog = pd.DataFrame(rows, columns=_CATALOG_COLUMNS)
    if catalog.empty:
        return catalog

    catalog = catalog.sort_values(["dataset", "channel", "temp_C", "type", "date", "cycle", "weeks"]).reset_index(
        drop=True
    )
    return catalog


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _dataset_for_path(path: Path, roots: dict[str, Path]) -> str:
    for dataset, root in roots.items():
        if _is_relative_to(path, Path(root)):
            return dataset
    raise ValueError(f"path is not inside the configured KIER roots: {path}")


def _row_for_file(path: Path, roots: dict[str, Path]) -> dict:
    dataset = _dataset_for_path(path, roots)
    if dataset == "main_cell":
        row = _parse_main_cell_file(path)
    elif dataset == "pouch_soh":
        row = _parse_pouch_file(path)
    else:
        row = _parse_module_file(path)
        if row is None and path.parent.parent.name == "Pattern":
            row = _row_for_module_pattern_base(path)
    if row is None:
        raise ValueError(f"unsupported or ignored KIER path: {path}")
    return row


def _row_for_module_pattern_base(path: Path) -> dict:
    match = _MODULE_FILE_RE.match(path.name)
    dir_match = _MODULE_DIR_RE.match(path.parent.name)
    if not match or not dir_match:
        raise ValueError(f"unsupported module pattern file: {path}")
    chunk_paths = [item.resolve() for item in sorted(path.parent.glob("*.csv"), key=_module_chunk_key)]
    row = _empty_row("module")
    row.update(
        {
            "channel": match.group("channel"),
            "temp_C": int(dir_match.group("temp")),
            "cycle": int(dir_match.group("cycle")),
            "type": "Pattern",
            "date": _date_yyyy_to_iso(dir_match.group("date")),
            "file_path": str(path.resolve()),
            "pattern_chunks": chunk_paths,
        }
    )
    return row


def _resolve_module_pattern_base(path: Path) -> Path:
    match = _MODULE_FILE_RE.match(path.name)
    if not match:
        return path
    if match.group("chunk") is None:
        return path
    base_name = path.name.replace(f"({match.group('chunk')})", "")
    return path.with_name(base_name)


def merge_pattern_chunks(chunk_paths: Sequence[Path | str]) -> pd.DataFrame:
    """Merge module pattern chunk files into one continuous dataframe."""
    merged: list[pd.DataFrame] = []
    prev_last_time: float | None = None
    prev_last_step: int | None = None
    prev_dt: float = 1.0

    for chunk_path in sorted((Path(item) for item in chunk_paths), key=_module_chunk_key):
        df = read_cycler_file(str(chunk_path)).sort_values("time_s").reset_index(drop=True)
        if prev_last_time is not None:
            time_jump = float(df["time_s"].iloc[0] - prev_last_time)
            expected_jump = prev_dt
            if abs(time_jump - expected_jump) > 1e-6:
                df["time_s"] = df["time_s"] + (prev_last_time + expected_jump - float(df["time_s"].iloc[0]))
            if prev_last_step is not None and int(df["step"].iloc[0]) < prev_last_step:
                df["step"] = df["step"] + (prev_last_step - int(df["step"].iloc[0]))
            df = df[df["time_s"] > prev_last_time].reset_index(drop=True)

        if len(df) >= 2:
            prev_dt = float(df["time_s"].diff().dropna().median())
            if not prev_dt or prev_dt <= 0:
                prev_dt = 1.0
        prev_last_time = float(df["time_s"].iloc[-1])
        prev_last_step = int(df["step"].iloc[-1])
        merged.append(df)

    if not merged:
        return pd.DataFrame(columns=["time_s", "voltage", "current", "step"])
    return pd.concat(merged, ignore_index=True)


def load_kier_run(file_path: str, merge_chunks: bool = True) -> dict:
    """Load a single KIER run and return a normalized dataframe plus metadata."""
    path = Path(file_path).resolve()
    roots = {name: Path(root) for name, root in SCAN_ROOTS.items()}
    dataset = _dataset_for_path(path, roots)

    if dataset == "module" and "Pattern" in path.parts and merge_chunks:
        base_path = _resolve_module_pattern_base(path)
        row = _row_for_module_pattern_base(base_path)
        chunk_paths = row["pattern_chunks"] or [base_path]
        df = merge_pattern_chunks(chunk_paths)
        n_chunks = len(chunk_paths)
        schema_variant = "module_days_hms"
    else:
        row = _row_for_file(path, roots)
        df = read_cycler_file(str(path))
        n_chunks = 1
        schema_variant = {
            "main_cell": "pne_hms",
            "pouch_soh": "pouch_minutes",
            "module": "module_days_hms",
        }[dataset]

    meta = {
        "dataset": row["dataset"],
        "channel": row["channel"],
        "temp_C": row["temp_C"],
        "cycle": row["cycle"],
        "weeks": row["weeks"],
        "type": row["type"],
        "date": row["date"],
        "n_chunks": n_chunks,
        "schema_variant": schema_variant,
    }
    return {"df": df, "meta": meta}


def _format_value(value) -> str:
    if pd.isna(value):
        return "-"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _build_summary_markdown(catalog: pd.DataFrame) -> str:
    if catalog.empty:
        return "# catalog_summary_v0\n\nNo rows found.\n"

    lines = ["# catalog_summary_v0", ""]
    for dataset in catalog["dataset"].dropna().unique():
        subset = catalog[catalog["dataset"] == dataset].copy()
        lines.append(f"## {dataset}")
        lines.append("")
        lines.append("| channel | temp_C | type | cycle_grid | weeks_grid | files |")
        lines.append("|---|---:|---|---|---|---:|")
        grouped = subset.groupby(["channel", "temp_C", "type"], dropna=False)
        for (channel, temp_c, type_name), group in grouped:
            cycle_grid = ",".join(str(int(v)) for v in sorted(group["cycle"].dropna().unique()))
            weeks_grid = ",".join(str(int(v)) for v in sorted(group["weeks"].dropna().unique()))
            lines.append(
                "| "
                + " | ".join(
                    [
                        _format_value(channel),
                        _format_value(temp_c),
                        _format_value(type_name),
                        cycle_grid or "-",
                        weeks_grid or "-",
                        str(len(group)),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def dump_catalog_artifacts(
    catalog_csv: str | Path | None = None,
    summary_md: str | Path | None = None,
    roots: dict | None = None,
) -> pd.DataFrame:
    """Build the KIER catalog and write the Stage 0 CSV/summary artifacts."""
    catalog = list_kier_files(roots=roots)
    catalog_csv = Path(catalog_csv or (KIER_ROOT / "outputs" / "catalog_kier_v0.csv"))
    summary_md = Path(summary_md or (KIER_ROOT / "outputs" / "catalog_summary_v0.md"))
    catalog_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_md.parent.mkdir(parents=True, exist_ok=True)

    serializable = catalog.copy()
    if not serializable.empty:
        serializable["pattern_chunks"] = serializable["pattern_chunks"].apply(
            lambda items: ";".join(str(Path(item)) for item in items) if isinstance(items, list) else ""
        )
    serializable.to_csv(catalog_csv, index=False, encoding="utf-8-sig")
    summary_md.write_text(_build_summary_markdown(catalog), encoding="utf-8")
    return catalog


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or [])
    catalog_csv = args[0] if len(args) >= 1 else None
    summary_md = args[1] if len(args) >= 2 else None
    catalog = dump_catalog_artifacts(catalog_csv=catalog_csv, summary_md=summary_md)
    print(f"catalog rows: {len(catalog)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
