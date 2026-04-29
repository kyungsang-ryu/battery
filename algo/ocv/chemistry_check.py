"""Lightweight chemistry sanity-check heuristics for dQ/dV curves."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from algo.data_io import read_cycler_file
from algo.ocv.ocv_soc import compute_dqdv


def classify_chemistry(dqdv_df: pd.DataFrame) -> dict:
    """Classify chemistry using broad dQ/dV peak windows."""
    if dqdv_df.empty:
        return {"label": "unknown", "confidence": 0.0, "peaks": [], "reason": "empty dQ/dV"}

    work = dqdv_df.dropna(subset=["V", "dQdV"]).copy()
    if work.empty:
        return {"label": "unknown", "confidence": 0.0, "peaks": [], "reason": "all NaN dQ/dV"}

    work["abs_dqdv"] = work["dQdV"].abs()
    peak_candidates = work.sort_values("abs_dqdv", ascending=False).head(8)
    peaks = []
    for _, row in peak_candidates.iterrows():
        voltage = float(row["V"])
        if all(abs(voltage - item["V"]) > 0.03 for item in peaks):
            peaks.append({"V": voltage, "height": float(row["abs_dqdv"])})
    peaks.sort(key=lambda item: item["V"])

    peak_vs = [item["V"] for item in peaks]
    in_ncm_low = any(3.55 <= value <= 3.85 for value in peak_vs)
    in_ncm_high = any(3.85 <= value <= 4.05 for value in peak_vs)
    in_lfp = any(3.20 <= value <= 3.45 for value in peak_vs)

    if in_ncm_low and in_ncm_high:
        return {
            "label": "NCM",
            "confidence": 0.82,
            "peaks": peaks,
            "reason": "peaks appear in both mid-voltage and high-voltage NCM windows",
        }
    if (in_ncm_low or in_ncm_high) and not in_lfp:
        return {
            "label": "NCM",
            "confidence": 0.58,
            "peaks": peaks,
            "reason": "at least one dominant peak appears in the NCM voltage window and no strong LFP plateau is detected",
        }
    if in_lfp and not in_ncm_high:
        return {
            "label": "LFP",
            "confidence": 0.60,
            "peaks": peaks,
            "reason": "dominant activity is concentrated near the LFP plateau window",
        }
    return {
        "label": "unknown",
        "confidence": 0.35 if peaks else 0.0,
        "peaks": peaks,
        "reason": "peak structure does not strongly match the built-in NCM/LFP windows",
    }


def extract_discharge_dqdv(file_path: str | Path, nominal_capacity_ah: float = 63.0) -> pd.DataFrame:
    """Build dQ/dV from the longest low-rate discharge step in an RPT file."""
    df = read_cycler_file(str(file_path))
    summary = (
        df.groupby("step", as_index=False)
        .agg(
            avg_current=("current", "mean"),
            duration=("time_s", lambda x: float(x.max() - x.min())),
        )
        .sort_values("duration", ascending=False)
    )

    max_low_rate_a = 0.2 * nominal_capacity_ah
    candidates = summary[
        (summary["avg_current"] < -1e-4)
        & (summary["avg_current"] > -max_low_rate_a)
        & (summary["duration"] >= 1800.0)
    ]
    if candidates.empty:
        raise RuntimeError("no low-rate discharge step longer than 1800 s found")

    best_step = candidates.iloc[0]["step"]
    sub = df[df["step"] == best_step].sort_values("time_s")
    return compute_dqdv(sub["voltage"], sub["current"], sub["time_s"])


def save_dqdv_plot(dqdv_df: pd.DataFrame, output_png: str | Path, title: str) -> None:
    """Save a simple dQ/dV PNG without external plotting dependencies."""
    width, height = 1200, 800
    margin_left, margin_right, margin_top, margin_bottom = 90, 40, 70, 70
    x0, y0 = margin_left, height - margin_bottom
    x1, y1 = width - margin_right, margin_top

    valid = dqdv_df.dropna(subset=["V", "dQdV"]).copy()
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle([x0, y1, x1, y0], outline="black", width=2)

    x_min = float(valid["V"].min())
    x_max = float(valid["V"].max())
    y_min = float(valid["dQdV"].min())
    y_max = float(valid["dQdV"].max())
    if y_min == y_max:
        y_min -= 1.0
        y_max += 1.0

    for value in np.linspace(round(x_min, 1), round(x_max, 1), 6):
        ratio = 0.0 if x_max == x_min else (value - x_min) / (x_max - x_min)
        x = x0 + (x1 - x0) * ratio
        draw.line([(x, y1), (x, y0)], fill=(225, 225, 225), width=1)
        draw.text((x - 10, y0 + 10), f"{value:.2f}", fill="black")

    for value in np.linspace(y_min, y_max, 7):
        ratio = 0.0 if y_max == y_min else (value - y_min) / (y_max - y_min)
        y = y0 - (y0 - y1) * ratio
        draw.line([(x0, y), (x1, y)], fill=(225, 225, 225), width=1)
        draw.text((10, y - 8), f"{value:.2f}", fill="black")

    points = []
    for _, row in valid.iterrows():
        x_ratio = 0.0 if x_max == x_min else (float(row["V"]) - x_min) / (x_max - x_min)
        y_ratio = 0.0 if y_max == y_min else (float(row["dQdV"]) - y_min) / (y_max - y_min)
        x = x0 + (x1 - x0) * x_ratio
        y = y0 - (y0 - y1) * y_ratio
        points.append((x, y))
    draw.line(points, fill=(31, 119, 180), width=3)

    draw.text((margin_left, 20), title, fill="black")
    draw.text((width // 2 - 40, height - 30), "Voltage (V)", fill="black")
    draw.text((10, 20), "dQ/dV", fill="black")

    output_png = Path(output_png)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_png)


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or [])
    if len(args) < 2:
        print(
            "usage: python -m algo.ocv.chemistry_check <input_csv> <output_png> [nominal_capacity_Ah]"
        )
        return 1
    input_path, output_png = args[:2]
    nominal_capacity_ah = float(args[2]) if len(args) >= 3 else 63.0
    dqdv_df = extract_discharge_dqdv(input_path, nominal_capacity_ah)
    result = classify_chemistry(dqdv_df)
    save_dqdv_plot(dqdv_df, output_png, title=Path(output_png).stem)
    import json

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
