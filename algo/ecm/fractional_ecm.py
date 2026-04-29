"""Fractional-order ECM identification for DCIR pulse files.

This KCI1 prototype uses a bounded stretched-exponential time response as a
fast, stable approximation of an R + CPE branch in the time domain.
"""

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
    values: list[np.ndarray] = []
    for frame in frames:
        if len(frame) >= 2:
            diffs = np.diff(frame["time_s"].to_numpy(dtype=float))
            diffs = diffs[diffs > 0]
            if diffs.size:
                values.append(diffs)
    if not values:
        return 1.0
    dt_s = float(np.median(np.concatenate(values)))
    return dt_s if np.isfinite(dt_s) and dt_s > 0 else 1.0


def _elapsed(frame: pd.DataFrame, dt_s: float) -> np.ndarray:
    times = frame["time_s"].to_numpy(dtype=float)
    return times - float(times[0]) + dt_s


def _fractional_charge(t_s: np.ndarray, tau_s: float, alpha: float) -> np.ndarray:
    scaled = np.maximum(t_s, 0.0) / max(float(tau_s), 1e-12)
    return 1.0 - np.exp(-(scaled**alpha))


def _fractional_decay(t_s: np.ndarray, tau_s: float, alpha: float) -> np.ndarray:
    scaled = np.maximum(t_s, 0.0) / max(float(tau_s), 1e-12)
    return np.exp(-(scaled**alpha))


def _predict_fractional(
    params: np.ndarray,
    current_a: float,
    v_pre: float,
    pulse_t: np.ndarray,
    rest_t: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    r0, r1, tau_s, alpha = params
    pulse_dynamic = r1 * _fractional_charge(pulse_t, tau_s=tau_s, alpha=alpha)
    pulse_v = v_pre - current_a * (r0 + pulse_dynamic)

    if rest_t.size == 0:
        return pulse_v, np.empty(0, dtype=float)

    end_dynamic_v = current_a * r1 * float(_fractional_charge(np.array([pulse_t[-1]]), tau_s, alpha)[0])
    rest_v = v_pre - end_dynamic_v * _fractional_decay(rest_t, tau_s=tau_s, alpha=alpha)
    return pulse_v, rest_v


def _grid_fractional_fit(
    current_a: float,
    v_pre: float,
    pulse_t: np.ndarray,
    rest_t: np.ndarray,
    observed: np.ndarray,
    alpha_bounds: tuple[float, float] = (0.3, 1.0),
) -> tuple[np.ndarray, np.ndarray]:
    y = v_pre - observed
    best_params: np.ndarray | None = None
    best_pred: np.ndarray | None = None
    best_score = float("inf")
    tau_min = max(0.2, float(np.min(np.diff(np.unique(pulse_t)))) if len(pulse_t) > 1 else 0.2)
    tau_max = max(200.0, float(pulse_t[-1]) * 30.0, float(rest_t[-1]) * 10.0 if rest_t.size else 200.0)
    alpha_grid = np.linspace(alpha_bounds[0], alpha_bounds[1], 71)
    tau_grid = np.geomspace(tau_min, tau_max, 90)

    for alpha in alpha_grid:
        for tau_s in tau_grid:
            pulse_charge = _fractional_charge(pulse_t, tau_s=tau_s, alpha=float(alpha))
            end_charge = float(_fractional_charge(np.array([pulse_t[-1]]), tau_s, float(alpha))[0])
            if rest_t.size:
                rest_decay = _fractional_decay(rest_t, tau_s=tau_s, alpha=float(alpha))
                a_r0 = np.concatenate([np.full_like(pulse_t, current_a), np.zeros_like(rest_t)])
                a_r1 = np.concatenate([current_a * pulse_charge, current_a * end_charge * rest_decay])
            else:
                a_r0 = np.full_like(pulse_t, current_a)
                a_r1 = current_a * pulse_charge
            design = np.column_stack([a_r0, a_r1])
            try:
                r0, r1 = np.linalg.lstsq(design, y, rcond=None)[0]
            except np.linalg.LinAlgError:
                continue
            r0 = float(np.clip(r0, 1e-5, 1e-2))
            r1 = float(np.clip(r1, 1e-5, 1e-2))
            params = np.array([r0, r1, float(tau_s), float(alpha)], dtype=float)
            pulse_v, rest_v = _predict_fractional(params, current_a, v_pre, pulse_t, rest_t)
            predicted = np.concatenate([pulse_v, rest_v])
            residual = predicted - observed
            score = float(np.dot(residual, residual))
            if score < best_score:
                best_params = params
                best_pred = predicted
                best_score = score

    if best_params is None or best_pred is None:
        raise RuntimeError("fractional grid search failed")
    return best_params, best_pred


def _fit_fractional(
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
    r1_guess = float(np.clip(base.get("R1") or 1e-3, 1e-5, 1e-2))
    tau_guess = float(base.get("meta", {}).get("tau_s") or max(float(pulse_t[-1]), 10.0))
    x0 = np.array([r0_guess, r1_guess, np.clip(tau_guess, 0.1, 5.0e4), 0.85], dtype=float)

    if _scipy_least_squares is None:
        params, predicted = _grid_fractional_fit(current_a, v_pre, pulse_t, rest_t, observed)
    else:
        def residual(params: np.ndarray) -> np.ndarray:
            pulse_v, rest_v = _predict_fractional(params, current_a, v_pre, pulse_t, rest_t)
            return np.concatenate([pulse_v, rest_v]) - observed

        fit = _least_squares(
            residual,
            x0,
            bounds=(
                np.array([1e-5, 1e-5, 0.1, 0.3], dtype=float),
                np.array([1e-2, 1e-2, 5.0e4, 1.0], dtype=float),
            ),
            max_nfev=2000,
        )
        params = fit.x
        predicted = observed + fit.fun
    rmse_v = float(np.sqrt(np.mean((observed - predicted) ** 2)))
    return params, rmse_v, pulse_t, rest_t, observed, predicted


def identify_fractional(file_path: str | Path, nominal_capacity_ah: float = 63.0) -> dict:
    """Estimate a fractional-order R + CPE ECM from a DCIR pulse file."""
    df = read_cycler_file(str(file_path))
    pre_rest, pulse, post_rest = _select_segments(df)
    base = identify_1rc(file_path, nominal_capacity_ah=nominal_capacity_ah)
    quality = _segment_quality(pre_rest, pulse, post_rest)
    if not quality["sufficient_dynamic_samples"]:
        return {
            "model": "FOM",
            "R0": base["R0"],
            "R1": None,
            "C1_eq": None,
            "alpha": None,
            "rmse_V": None,
            "meta": {
                **base["meta"],
                **quality,
                "Q": None,
                "approximation": "bounded stretched-exponential R+CPE time response",
                "note": "FOM dynamic fit skipped because pulse/recovery samples are insufficient.",
            },
        }
    params, rmse_v, pulse_t, _rest_t, observed, predicted = _fit_fractional(pre_rest, pulse, post_rest, base)
    r0, r1, tau_s, alpha = (float(item) for item in params)
    c1_eq = tau_s / r1 if r1 > 0 else float("nan")
    q_cpe = (tau_s**alpha) / r1 if r1 > 0 else float("nan")

    pulse_rows = pulse[np.abs(pulse["current"]) > 1e-6].copy()
    current_a = float(abs(pulse_rows["current"].median()))

    return {
        "model": "FOM",
        "R0": r0,
        "R1": r1,
        "C1_eq": float(c1_eq),
        "alpha": alpha,
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
            "tau_s": tau_s,
            "Q": float(q_cpe),
            "temp_C": float(df["temperature"].dropna().mean()) if "temperature" in df.columns else None,
            "fit_points": int(len(observed)),
            "fit_rmse_check_V": float(np.sqrt(np.mean((observed - predicted) ** 2))),
            "approximation": "bounded stretched-exponential R+CPE time response",
        },
    }


__all__ = ["identify_fractional"]
