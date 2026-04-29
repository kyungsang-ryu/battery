"""Extract and export OCV lookup tables from RPT files."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from algo.ocv.ocv_soc import extract_ocv_soc_from_rpt


def build_lookup_table(curves: Mapping[str, pd.DataFrame], soc_step: int = 1) -> pd.DataFrame:
    """Interpolate discharge/charge curves to a regular SOC grid."""
    soc_grid = np.arange(0, 100 + soc_step, soc_step, dtype=float)
    lookup = pd.DataFrame({"SOC_pct": soc_grid})

    discharge = curves.get("discharge")
    charge = curves.get("charge")

    def _interp(curve: pd.DataFrame | None) -> np.ndarray:
        if curve is None or curve.empty:
            return np.full_like(soc_grid, np.nan)
        ordered = curve.sort_values("SOC")
        return np.interp(
            soc_grid,
            ordered["SOC"].to_numpy(dtype=float),
            ordered["OCV"].to_numpy(dtype=float),
        )

    discharge_v = _interp(discharge)
    charge_v = _interp(charge)
    if np.all(np.isnan(charge_v)):
        avg_v = discharge_v.copy()
    elif np.all(np.isnan(discharge_v)):
        avg_v = charge_v.copy()
    else:
        avg_v = np.nanmean(np.vstack([discharge_v, charge_v]), axis=0)

    lookup["OCV_discharge_V"] = discharge_v
    lookup["OCV_charge_V"] = charge_v
    lookup["OCV_avg_V"] = avg_v
    return lookup


def save_lookup_plot(lookup: pd.DataFrame, output_png: Path, title: str) -> None:
    """Save a lightweight PNG plot without external plotting dependencies."""
    width, height = 1200, 800
    margin_left, margin_right, margin_top, margin_bottom = 90, 40, 70, 70
    x0, y0 = margin_left, height - margin_bottom
    x1, y1 = width - margin_right, margin_top

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    series = []
    colors = {
        "OCV_discharge_V": (31, 119, 180),
        "OCV_charge_V": (214, 39, 40),
        "OCV_avg_V": (44, 160, 44),
    }
    for column in ["OCV_discharge_V", "OCV_charge_V", "OCV_avg_V"]:
        valid = lookup[["SOC_pct", column]].dropna()
        if not valid.empty:
            series.append((column, valid))

    y_min = min(float(valid[column].min()) for column, valid in series) - 0.05
    y_max = max(float(valid[column].max()) for column, valid in series) + 0.05
    y_min = min(y_min, 3.0)
    y_max = max(y_max, 4.2)

    draw.rectangle([x0, y1, x1, y0], outline="black", width=2)

    for soc in range(0, 101, 20):
        x = x0 + (x1 - x0) * (soc / 100.0)
        draw.line([(x, y1), (x, y0)], fill=(225, 225, 225), width=1)
        draw.text((x - 10, y0 + 10), str(soc), fill="black")

    y_ticks = np.linspace(y_min, y_max, 7)
    for value in y_ticks:
        ratio = 0.0 if y_max == y_min else (value - y_min) / (y_max - y_min)
        y = y0 - (y0 - y1) * ratio
        draw.line([(x0, y), (x1, y)], fill=(225, 225, 225), width=1)
        draw.text((10, y - 8), f"{value:.2f}", fill="black")

    for column, valid in series:
        points = []
        for _, row in valid.iterrows():
            x = x0 + (x1 - x0) * (float(row["SOC_pct"]) / 100.0)
            ratio = 0.0 if y_max == y_min else (float(row[column]) - y_min) / (y_max - y_min)
            y = y0 - (y0 - y1) * ratio
            points.append((x, y))
        draw.line(points, fill=colors[column], width=3)

    draw.text((margin_left, 20), title, fill="black")
    draw.text((width // 2 - 40, height - 30), "SOC (%)", fill="black")
    draw.text((10, 20), "OCV (V)", fill="black")

    legend_x = width - 260
    legend_y = 20
    for index, column in enumerate(["OCV_discharge_V", "OCV_charge_V", "OCV_avg_V"]):
        draw.line(
            [(legend_x, legend_y + 25 * index), (legend_x + 30, legend_y + 25 * index)],
            fill=colors[column],
            width=3,
        )
        draw.text((legend_x + 40, legend_y - 8 + 25 * index), column, fill="black")

    output_png.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_png)


def run_extract(
    input_path: str | Path,
    output_csv: str | Path,
    output_png: str | Path,
    nominal_capacity_ah: float = 63.0,
) -> pd.DataFrame:
    curves = extract_ocv_soc_from_rpt(str(input_path), nominal_capacity_ah)
    if "error" in curves:
        raise RuntimeError(curves["error"])
    lookup = build_lookup_table(curves)
    output_csv = Path(output_csv)
    output_png = Path(output_png)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    lookup.to_csv(output_csv, index=False, encoding="utf-8-sig")
    save_lookup_plot(lookup, output_png, title=output_csv.stem)
    return lookup


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or [])
    if len(args) < 3:
        print(
            "usage: python -m algo.runners.run_ocv_extract <input_csv> <output_csv> <output_png> [nominal_capacity_Ah]"
        )
        return 1
    input_path, output_csv, output_png = args[:3]
    nominal_capacity_ah = float(args[3]) if len(args) >= 4 else 63.0
    run_extract(input_path, output_csv, output_png, nominal_capacity_ah)
    print(output_csv)
    print(output_png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
