"""Run ECM identification over one or more DCIR files."""

from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path
from typing import Callable, Sequence

import numpy as np
import pandas as pd

try:
    from scipy.stats import spearmanr as _scipy_spearmanr
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal local runtimes.
    _scipy_spearmanr = None

from algo.ecm.ecm_2rc import identify_2rc
from algo.ecm.ecm_identify import identify_1rc
from algo.ecm.fractional_ecm import identify_fractional

IDENTIFIERS: dict[str, Callable[[str | Path, float], dict]] = {
    "1RC": identify_1rc,
    "2RC": identify_2rc,
    "FOM": identify_fractional,
}


def _spearmanr(x: pd.Series, y: pd.Series) -> tuple[float, float]:
    if _scipy_spearmanr is not None:
        rho, p_value = _scipy_spearmanr(x, y)
        return float(rho), float(p_value)
    rho = float(pd.Series(x).rank().corr(pd.Series(y).rank()))
    return rho, float("nan")


def _infer_cycle(path: Path, result: dict) -> int | None:
    meta = result.get("meta", {})
    if meta.get("cycle") is not None:
        return int(meta["cycle"])
    match = re.search(r"_(\d+)(?:cycle|Cycle)\b", path.name)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d{2,5})cycle", str(path), flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _flatten_result(path: Path, result: dict) -> dict:
    meta = result.get("meta", {})
    row = {
        "model": result.get("model"),
        "file_path": str(path.resolve()),
        "cycle": _infer_cycle(path, result),
        "temp_C": meta.get("temp_C"),
        "R0": result.get("R0"),
        "R1": result.get("R1"),
        "C1": result.get("C1"),
        "R2": result.get("R2"),
        "C2": result.get("C2"),
        "C1_eq": result.get("C1_eq"),
        "alpha": result.get("alpha"),
        "Q": meta.get("Q"),
        "rmse_V": result.get("rmse_V"),
        "pulse_current_A": meta.get("pulse_current_A"),
        "pulse_duration_s": meta.get("pulse_duration_s"),
        "pulse_nonzero_samples": meta.get("pulse_nonzero_samples"),
        "recovery_samples": meta.get("recovery_samples"),
        "sufficient_dynamic_samples": meta.get("sufficient_dynamic_samples"),
        "fit_quality_flag": meta.get("fit_quality_flag"),
    }
    return row


def _expand_file_patterns(patterns: Sequence[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = [Path(item) for item in glob.glob(pattern)]
        if matches:
            paths.extend(matches)
            continue
        candidate = Path(pattern)
        if candidate.exists():
            paths.append(candidate)
    return sorted(set(path.resolve() for path in paths), key=lambda p: str(p))


def _write_report(results: pd.DataFrame, output_dir: Path) -> None:
    lines = ["# K1 ECM Identification Report", ""]
    if results.empty:
        lines.append("No successful identification results.")
        output_dir.joinpath("REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Files fitted: {len(results)}")
    lines.append(f"- Model: {results['model'].iloc[0]}")
    lines.append(f"- Mean RMSE_V: {results['rmse_V'].mean():.6g}")
    lines.append(f"- Median RMSE_V: {results['rmse_V'].median():.6g}")

    if "alpha" in results.columns and results["alpha"].notna().sum() >= 3 and results["cycle"].notna().sum() >= 3:
        valid = results.dropna(subset=["cycle", "alpha"])
        rho, p_value = _spearmanr(valid["cycle"], valid["alpha"])
        p_text = "nan" if np.isnan(p_value) else f"{p_value:.4g}"
        lines.append(f"- Spearman rho(cycle, alpha): {rho:.4f} (p={p_text})")

    lines.append("")
    lines.append("## Per-Cycle Results")
    lines.append("")
    display_cols = [col for col in ["cycle", "temp_C", "R0", "R1", "R2", "alpha", "rmse_V", "file_path"] if col in results]
    lines.append("| " + " | ".join(display_cols) + " |")
    lines.append("|" + "|".join("---" for _ in display_cols) + "|")
    for _, row in results[display_cols].iterrows():
        values = []
        for col in display_cols:
            value = row[col]
            if isinstance(value, float):
                values.append("" if np.isnan(value) else f"{value:.6g}")
            elif pd.isna(value):
                values.append("")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    output_dir.joinpath("REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_ecm_identify(
    model: str,
    file_patterns: Sequence[str],
    output_dir: str | Path,
    nominal_capacity_ah: float = 63.0,
    force: bool = False,
    merge_existing: bool = True,
) -> pd.DataFrame:
    """Run ECM identification and write params_per_cycle.csv plus JSON details."""
    model_key = model.upper()
    if model_key not in IDENTIFIERS:
        raise ValueError(f"unsupported model: {model}")

    output_dir = Path(output_dir)
    params_csv = output_dir / "params_per_cycle.csv"

    files = _expand_file_patterns(file_patterns)
    if not files:
        raise FileNotFoundError(f"no files matched: {list(file_patterns)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    details_dir = output_dir / "details"
    details_dir.mkdir(exist_ok=True)
    identifier = IDENTIFIERS[model_key]

    rows: list[dict] = []
    failures: list[dict] = []
    for path in files:
        try:
            result = identifier(path, nominal_capacity_ah)
            rows.append(_flatten_result(path, result))
            detail_name = f"{path.stem}_{model_key.lower()}.json"
            details_dir.joinpath(detail_name).write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:  # Keep batch runs moving while preserving evidence.
            failures.append({"file_path": str(path), "error": repr(exc)})

    results = pd.DataFrame(rows)
    if merge_existing and params_csv.exists() and not force:
        existing = pd.read_csv(params_csv)
        results = pd.concat([existing, results], ignore_index=True, sort=False)
        dedupe_cols = [col for col in ["model", "cycle", "file_path"] if col in results.columns]
        if dedupe_cols:
            results = results.drop_duplicates(subset=dedupe_cols, keep="last")
    if not results.empty:
        results = results.sort_values(["cycle", "file_path"], na_position="last").reset_index(drop=True)
    results.to_csv(params_csv, index=False, encoding="utf-8-sig")
    if failures:
        pd.DataFrame(failures).to_csv(output_dir / "failures.csv", index=False, encoding="utf-8-sig")
    _write_report(results, output_dir)
    return results


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(IDENTIFIERS), required=True)
    parser.add_argument("--files", action="append", required=True, help="Input file path or glob. Repeatable.")
    parser.add_argument("--out", required=True, help="Output run directory.")
    parser.add_argument("--nominal-capacity-ah", type=float, default=63.0)
    parser.add_argument("--force", action="store_true", help="Overwrite params_per_cycle.csv if it exists.")
    parser.add_argument("--no-merge", action="store_true", help="Do not append/update an existing params CSV.")
    args = parser.parse_args(argv)

    results = run_ecm_identify(
        model=args.model,
        file_patterns=args.files,
        output_dir=args.out,
        nominal_capacity_ah=args.nominal_capacity_ah,
        force=args.force,
        merge_existing=not args.no_merge,
    )
    print(f"wrote {len(results)} rows to {Path(args.out) / 'params_per_cycle.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
