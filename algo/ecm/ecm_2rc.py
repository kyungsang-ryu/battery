"""2-RC equivalent circuit identification for DCIR pulse files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.optimize import least_squares as _scipy_least_squares
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal local runtimes.
    _scipy_least_squares = None

from algo.data_io import read_cycler_file
from algo.ecm.ecm_identify import _segment_quality, _select_segments, identify_1rc


class _FitResult:
    def __init__(self, x: np.ndarray, fun: np.ndarray):
        self.x = x
        self.fun = fun


def _least_squares(residual, x0: np.ndarray, bounds: tuple[np.ndarray, np.ndarray], max_nfev: int) -> _FitResult:
    if _scipy_least_squares is not None:
        fit = _scipy_least_squares(residual, x0, bounds=bounds, method="trf", max_nfev=max_nfev)
        return _FitResult(np.asarray(fit.x, dtype=float), np.asarray(fit.fun, dtype=float))

    lower, upper = bounds
    best = np.clip(np.asarray(x0, dtype=float), lower, upper)
    best_fun = np.asarray(residual(best), dtype=float)
    best_score = float(np.dot(best_fun, best_fun))
    step = np.maximum((upper - lower) * 0.10, 1e-12)
    evaluations = 1
    while evaluations < max_nfev and float(np.max(step)) > 1e-9:
        improved = False
        for idx in range(best.size):
            for direction in (1.0, -1.0):
                trial = best.copy()
                trial[idx] = np.clip(trial[idx] + direction * step[idx], lower[idx], upper[idx])
                trial_fun = np.asarray(residual(trial), dtype=float)
                trial_score = float(np.dot(trial_fun, trial_fun))
                evaluations += 1
                if trial_score < best_score:
                    best, best_fun, best_score = trial, trial_fun, trial_score
                    improved = True
                if evaluations >= max_nfev:
                    break
            if evaluations >= max_nfev:
                break
        if not improved:
            step *= 0.5
    return _FitResult(best, best_fun)


def _median_dt_s(*frames: pd.DataFrame) -> float:
    diffs: list[np.ndarray] = []
    for frame in frames:
        if len(frame) >= 2:
            values = np.diff(frame["time_s"].to_numpy(dtype=float))
            values = values[values > 0]
            if values.size:
                diffs.append(values)
    if not diffs:
        return 1.0
    dt = float(np.median(np.concatenate(diffs)))
    return dt if np.isfinite(dt) and dt > 0 else 1.0


def _elapsed(frame: pd.DataFrame, dt_s: float) -> np.ndarray:
    values = frame["time_s"].to_numpy(dtype=float)
    return values - float(values[0]) + dt_s


def _split_ordered_branches(r1: float, tau1: float, r2: float, tau2: float) -> tuple[float, float, float, float]:
    if tau1 <= tau2:
        return r1, tau1, r2, tau2
    return r2, tau2, r1, tau1


def _predict_2rc(
    params: np.ndarray,
    current_a: float,
    v_pre: float,
    pulse_t: np.ndarray,
    rest_t: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    r0, r1, tau1, r2, tau2 = params
    pulse_branch_1 = r1 * (1.0 - np.exp(-pulse_t / tau1))
    pulse_branch_2 = r2 * (1.0 - np.exp(-pulse_t / tau2))
    pulse_v = v_pre - current_a * (r0 + pulse_branch_1 + pulse_branch_2)

    if rest_t.size == 0:
        return pulse_v, np.empty(0, dtype=float)

    end_t = float(pulse_t[-1])
    end_1 = current_a * r1 * (1.0 - np.exp(-end_t / tau1))
    end_2 = current_a * r2 * (1.0 - np.exp(-end_t / tau2))
    rest_v = v_pre - end_1 * np.exp(-rest_t / tau1) - end_2 * np.exp(-rest_t / tau2)
    return pulse_v, rest_v


def _fit_2rc(
    pre_rest: pd.DataFrame,
    pulse: pd.DataFrame,
    post_rest: pd.DataFrame,
    base: dict,
) -> tuple[np.ndarray, float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    pulse_rows = pulse[np.abs(pulse["current"]) > 1e-6].copy().reset_index(drop=True)
    if pulse_rows.empty:
        raise RuntimeError("dominant pulse step does not contain non-zero current samples")

    post_rows = post_rest.copy().reset_index(drop=True)
    current_a = float(abs(pulse_rows["current"].median()))
    v_pre = float(pre_rest["voltage"].tail(min(3, len(pre_rest))).mean())
    dt_s = _median_dt_s(pre_rest, pulse_rows, post_rows)
    pulse_t = _elapsed(pulse_rows, dt_s)
    if post_rows.empty:
        rest_t = np.empty(0, dtype=float)
    else:
        rest_t = post_rows["time_s"].to_numpy(dtype=float) - float(pulse["time_s"].iloc[-1])
        rest_t = rest_t[rest_t > 0]
        post_rows = post_rows.tail(len(rest_t)).reset_index(drop=True)

    observed_pulse = pulse_rows["voltage"].to_numpy(dtype=float)
    observed_rest = post_rows["voltage"].to_numpy(dtype=float) if len(post_rows) else np.empty(0, dtype=float)
    observed = np.concatenate([observed_pulse, observed_rest])

    r0_guess = float(np.clip(base.get("R0") or 1e-3, 1e-5, 1e-2))
    r_total = float(np.clip(base.get("R1") or 1e-3, 2e-5, 2e-2))
    tau_guess = float(base.get("meta", {}).get("tau_s") or max(float(pulse_t[-1]), 10.0))
    x0 = np.array(
        [
            r0_guess,
            np.clip(0.65 * r_total, 1e-5, 1e-2),
            np.clip(0.35 * tau_guess, 0.1, 5.0e4),
            np.clip(0.35 * r_total, 1e-5, 1e-2),
            np.clip(2.5 * tau_guess, 0.1, 5.0e4),
        ],
        dtype=float,
    )

    def residual(params: np.ndarray) -> np.ndarray:
        pulse_v, rest_v = _predict_2rc(params, current_a, v_pre, pulse_t, rest_t)
        return np.concatenate([pulse_v, rest_v]) - observed

    fit = _least_squares(
        residual,
        x0,
        bounds=(
            np.array([1e-5, 1e-5, 0.1, 1e-5, 0.1], dtype=float),
            np.array([1e-2, 1e-2, 5.0e4, 1e-2, 5.0e4], dtype=float),
        ),
        max_nfev=2000,
    )
    predicted = observed + fit.fun
    rmse_v = float(np.sqrt(np.mean((observed - predicted) ** 2)))
    return fit.x, rmse_v, pulse_t, rest_t, observed, predicted


def identify_2rc(file_path: str | Path, nominal_capacity_ah: float = 63.0) -> dict:
    """Estimate a 2-RC ECM from a DCIR pulse file."""
    df = read_cycler_file(str(file_path))
    pre_rest, pulse, post_rest = _select_segments(df)
    base = identify_1rc(file_path, nominal_capacity_ah=nominal_capacity_ah)
    quality = _segment_quality(pre_rest, pulse, post_rest)
    if not quality["sufficient_dynamic_samples"]:
        return {
            "model": "2RC",
            "R0": base["R0"],
            "R1": None,
            "C1": None,
            "R2": None,
            "C2": None,
            "rmse_V": None,
            "meta": {
                **base["meta"],
                **quality,
                "note": "2-RC dynamic fit skipped because pulse/recovery samples are insufficient.",
            },
        }
    params, rmse_v, pulse_t, rest_t, observed, predicted = _fit_2rc(pre_rest, pulse, post_rest, base)
    r0, r1, tau1, r2, tau2 = params
    r1, tau1, r2, tau2 = _split_ordered_branches(float(r1), float(tau1), float(r2), float(tau2))
    c1 = tau1 / r1 if r1 > 0 else float("nan")
    c2 = tau2 / r2 if r2 > 0 else float("nan")

    pulse_rows = pulse[np.abs(pulse["current"]) > 1e-6].copy()
    current_a = float(abs(pulse_rows["current"].median()))

    return {
        "model": "2RC",
        "R0": float(r0),
        "R1": float(r1),
        "C1": float(c1),
        "R2": float(r2),
        "C2": float(c2),
        "rmse_V": rmse_v,
        "meta": {
            **quality,
            "file_path": str(Path(file_path).resolve()),
            "nominal_capacity_ah": float(nominal_capacity_ah),
            "pre_rest_step": int(pre_rest["step"].iloc[0]),
            "pulse_step": int(pulse["step"].iloc[0]),
            "post_rest_step": int(post_rest["step"].iloc[0]),
            "pulse_current_A": current_a,
            "pulse_duration_s": float(pulse_t[-1]) if pulse_t.size else 0.0,
            "tau1_s": float(tau1),
            "tau2_s": float(tau2),
            "temp_C": float(df["temperature"].dropna().mean()) if "temperature" in df.columns else None,
            "fit_points": int(len(observed)),
            "fit_rmse_check_V": float(np.sqrt(np.mean((observed - predicted) ** 2))),
        },
    }


__all__ = ["identify_2rc"]
