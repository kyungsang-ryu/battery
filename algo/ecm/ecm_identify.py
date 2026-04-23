"""Lightweight 1-RC identification for DCIR files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

from algo.data_io import read_cycler_file


def _step_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("step", as_index=False)
        .agg(
            current_mean=("current", "mean"),
            current_abs=("current", lambda x: float(np.abs(x).mean())),
            time_start=("time_s", "min"),
            time_end=("time_s", "max"),
        )
        .sort_values("time_start")
        .reset_index(drop=True)
    )
    summary["duration"] = summary["time_end"] - summary["time_start"]
    return summary


def _select_segments(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary = _step_summary(df)
    pulse_row = summary.sort_values(["current_abs", "duration"], ascending=[False, False]).iloc[0]
    pulse_idx = int(pulse_row.name)
    pulse_current = float(pulse_row["current_abs"])
    rest_threshold = max(0.05 * pulse_current, 0.1)

    pre_candidates = summary.iloc[:pulse_idx]
    pre_rest = pre_candidates[pre_candidates["current_abs"] <= rest_threshold]
    if pre_rest.empty:
        raise RuntimeError("no rest step found before the dominant pulse step")

    post_candidates = summary.iloc[pulse_idx + 1 :]
    post_rest = post_candidates[post_candidates["current_abs"] <= rest_threshold]
    if post_rest.empty:
        raise RuntimeError("no rest step found after the dominant pulse step")

    pre_step = int(pre_rest.iloc[-1]["step"])
    pulse_step = int(pulse_row["step"])
    post_step = int(post_rest.iloc[0]["step"])
    return (
        df[df["step"] == pre_step].sort_values("time_s").reset_index(drop=True),
        df[df["step"] == pulse_step].sort_values("time_s").reset_index(drop=True),
        df[df["step"] == post_step].sort_values("time_s").reset_index(drop=True),
    )


def _fit_recovery(rest_df: pd.DataFrame, current_a: float, t_origin: float) -> tuple[float, float]:
    if len(rest_df) < 4:
        return 0.0, float("nan")

    work = rest_df.copy()
    work["t_rel"] = work["time_s"] - float(t_origin)
    work = work[work["t_rel"] > 0.0].copy()
    if len(work) < 3:
        return 0.0, float("nan")

    v_inf = float(work["voltage"].tail(min(3, len(work))).mean())
    work["residual"] = v_inf - work["voltage"]
    work = work[work["residual"] > 1e-6]
    if len(work) < 2:
        return 0.0, float("nan")

    slope, intercept = np.polyfit(work["t_rel"], np.log(work["residual"]), 1)
    if slope >= 0:
        return 0.0, float("nan")

    tau_s = -1.0 / slope
    amplitude_v = float(np.exp(intercept))
    r1 = max(amplitude_v / max(abs(current_a), 1e-9), 0.0)
    return r1, tau_s


def identify_1rc(file_path: str | Path, nominal_capacity_ah: float = 63.0) -> dict:
    """Estimate a 1-RC ECM from a DCIR pulse file."""
    df = read_cycler_file(str(file_path))
    pre_rest, pulse, post_rest = _select_segments(df)

    pulse_rows = pulse[np.abs(pulse["current"]) > 1e-6].copy()
    if pulse_rows.empty:
        raise RuntimeError("dominant pulse step does not contain non-zero current samples")

    current_a = float(abs(pulse_rows["current"].median()))
    v_pre = float(pre_rest["voltage"].tail(min(3, len(pre_rest))).mean())
    v_pulse0 = float(pulse_rows["voltage"].iloc[0])
    r0 = max((v_pre - v_pulse0) / max(current_a, 1e-9), 0.0)

    post_rows = post_rest.copy()
    if len(post_rows) >= 2 and abs(float(post_rows["time_s"].iloc[0] - pulse["time_s"].iloc[-1])) < 1e-9:
        post_rows = post_rows.iloc[1:].reset_index(drop=True)
    r1, tau_s = _fit_recovery(post_rows, current_a, t_origin=float(pulse["time_s"].iloc[-1]))
    has_boundary_row = len(pulse) != len(pulse_rows)
    if np.isfinite(tau_s) and tau_s > 0 and r1 > 0 and not has_boundary_row:
        prev_rows = df[df["time_s"] < float(pulse_rows["time_s"].iloc[0])]
        delay_s = (
            float(pulse_rows["time_s"].iloc[0] - prev_rows["time_s"].iloc[-1])
            if not prev_rows.empty
            else 0.0
        )
        r0 = max(r0 - r1 * (1.0 - np.exp(-max(delay_s, 0.0) / tau_s)), 0.0)
    c1 = float(tau_s / r1) if r1 > 0 and np.isfinite(tau_s) else float("nan")

    pulse_t = pulse_rows["time_s"].to_numpy(dtype=float) - float(pulse_rows["time_s"].iloc[0])
    if np.isfinite(tau_s) and tau_s > 0 and r1 > 0:
        v_model_pulse = v_pre - current_a * (r0 + r1 * (1.0 - np.exp(-pulse_t / tau_s)))
    else:
        v_model_pulse = np.full(len(pulse_rows), v_pre - current_a * r0)

    observed = [pulse_rows["voltage"].to_numpy(dtype=float)]
    predicted = [v_model_pulse]

    if not post_rows.empty and np.isfinite(tau_s) and tau_s > 0 and r1 > 0:
        rest_t = post_rows["time_s"].to_numpy(dtype=float) - float(post_rows["time_s"].iloc[0])
        v_inf = float(post_rows["voltage"].tail(min(3, len(post_rows))).mean())
        amp_end = current_a * r1 * (1.0 - np.exp(-float(pulse_t[-1]) / tau_s))
        v_model_rest = v_inf - amp_end * np.exp(-rest_t / tau_s)
        observed.append(post_rows["voltage"].to_numpy(dtype=float))
        predicted.append(v_model_rest)

    observed_v = np.concatenate(observed)
    predicted_v = np.concatenate(predicted)
    rmse_v = float(np.sqrt(np.mean((observed_v - predicted_v) ** 2)))

    result = {
        "model": "1RC",
        "R0": float(r0),
        "R1": float(r1),
        "C1": float(c1) if np.isfinite(c1) else None,
        "rmse_V": rmse_v,
        "meta": {
            "file_path": str(Path(file_path).resolve()),
            "nominal_capacity_ah": float(nominal_capacity_ah),
            "pre_rest_step": int(pre_rest["step"].iloc[0]),
            "pulse_step": int(pulse["step"].iloc[0]),
            "post_rest_step": int(post_rest["step"].iloc[0]),
            "pulse_current_A": current_a,
            "pulse_duration_s": float(pulse_rows["time_s"].iloc[-1] - pulse_rows["time_s"].iloc[0]),
            "tau_s": float(tau_s) if np.isfinite(tau_s) else None,
            "temp_C": float(df["temperature"].dropna().mean()) if "temperature" in df.columns else None,
            "R0_mohm": float(r0 * 1000.0),
            "R1_mohm": float(r1 * 1000.0),
        },
    }
    return result


def identify_2rc(file_path: str | Path, nominal_capacity_ah: float = 63.0) -> dict:
    """Provide a conservative 2-RC-shaped placeholder based on the 1-RC fit."""
    base = identify_1rc(file_path, nominal_capacity_ah=nominal_capacity_ah)
    tau_s = base["meta"].get("tau_s") or 0.0
    r1 = float(base.get("R1") or 0.0)
    r_fast = r1 * 0.7
    r_slow = r1 * 0.3
    tau_fast = tau_s * 0.4 if tau_s else None
    tau_slow = tau_s * 2.0 if tau_s else None
    c1 = float(tau_fast / r_fast) if tau_fast and r_fast > 0 else None
    c2 = float(tau_slow / r_slow) if tau_slow and r_slow > 0 else None
    return {
        "model": "2RC",
        "R0": base["R0"],
        "R1": float(r_fast),
        "C1": c1,
        "R2": float(r_slow),
        "C2": c2,
        "rmse_V": base["rmse_V"],
        "meta": {
            **base["meta"],
            "note": "initial placeholder derived from the 1-RC fit; refine in a later task",
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or [])
    if not args:
        print("usage: python -m algo.ecm.ecm_identify <input_csv> [<output_json>] [<nominal_capacity_Ah>]")
        return 1

    input_path = args[0]
    output_path = None
    nominal_capacity_ah = 63.0
    if len(args) >= 2 and args[1].lower().endswith(".json"):
        output_path = args[1]
        if len(args) >= 3:
            nominal_capacity_ah = float(args[2])
    elif len(args) >= 2:
        nominal_capacity_ah = float(args[1])

    result = identify_1rc(input_path, nominal_capacity_ah=nominal_capacity_ah)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
