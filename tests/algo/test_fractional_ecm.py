"""Tests for KCI1 ECM identification models."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from algo.ecm.ecm_2rc import identify_2rc
from algo.ecm.ecm_identify import _segment_quality, _select_segments
from algo.ecm.fractional_ecm import identify_fractional
from algo.runners.run_ecm_identify import run_ecm_identify


def _fmt_time(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}.00"


def _write_2rc_sample(path: Path) -> None:
    r0 = 0.0018
    r1 = 0.0012
    r2 = 0.0008
    tau1 = 4.0
    tau2 = 28.0
    current_a = 10.0
    ocv = 3.72
    pulse_len = 80
    rest_len = 100

    lines = ["StepNo,Voltage(V),Current(A),TotTime(H:M:S)"]
    total_time = 0
    for _ in range(10):
        lines.append(f"2,{ocv:.8f},0.0,{_fmt_time(total_time)}")
        total_time += 1

    for k in range(pulse_len):
        t = k + 1
        voltage = ocv - current_a * (
            r0
            + r1 * (1.0 - np.exp(-t / tau1))
            + r2 * (1.0 - np.exp(-t / tau2))
        )
        lines.append(f"4,{voltage:.8f},{-current_a:.8f},{_fmt_time(total_time)}")
        total_time += 1

    end_1 = current_a * r1 * (1.0 - np.exp(-pulse_len / tau1))
    end_2 = current_a * r2 * (1.0 - np.exp(-pulse_len / tau2))
    for k in range(rest_len):
        t = k + 1
        voltage = ocv - end_1 * np.exp(-t / tau1) - end_2 * np.exp(-t / tau2)
        lines.append(f"5,{voltage:.8f},0.0,{_fmt_time(total_time)}")
        total_time += 1

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_fractional_sample(path: Path) -> None:
    r0 = 0.0017
    r1 = 0.0019
    tau = 18.0
    alpha = 0.72
    current_a = 10.0
    ocv = 3.72
    pulse_len = 90
    rest_len = 120

    def charge(t: float) -> float:
        return 1.0 - np.exp(-((t / tau) ** alpha))

    def decay(t: float) -> float:
        return np.exp(-((t / tau) ** alpha))

    lines = ["StepNo,Voltage(V),Current(A),TotTime(H:M:S)"]
    total_time = 0
    for _ in range(10):
        lines.append(f"2,{ocv:.8f},0.0,{_fmt_time(total_time)}")
        total_time += 1

    for k in range(pulse_len):
        t = k + 1
        voltage = ocv - current_a * (r0 + r1 * charge(t))
        lines.append(f"4,{voltage:.8f},{-current_a:.8f},{_fmt_time(total_time)}")
        total_time += 1

    end_dynamic_v = current_a * r1 * charge(pulse_len)
    for k in range(rest_len):
        t = k + 1
        voltage = ocv - end_dynamic_v * decay(t)
        lines.append(f"5,{voltage:.8f},0.0,{_fmt_time(total_time)}")
        total_time += 1

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_sparse_dcir_sample(path: Path) -> None:
    rows = [
        "StepNo,Voltage(V),Current(A),TotTime(H:M:S)",
        "2,3.700000,0.0,00:00:00.00",
        "2,3.700000,0.0,00:00:10.00",
        "3,3.690000,-6.3,00:00:20.00",
        "3,3.680000,-6.3,00:00:40.00",
        "4,3.640000,-63.0,00:00:50.00",
        "4,3.670000,0.0,00:01:00.00",
        "5,3.685000,0.0,00:01:10.00",
        "5,3.690000,0.0,00:01:20.00",
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_identify_2rc_synthetic(tmp_path: Path):
    sample = tmp_path / "sample_100cycle_2rc.csv"
    _write_2rc_sample(sample)

    result = identify_2rc(sample)

    assert result["model"] == "2RC"
    assert result["R0"] == pytest.approx(0.0018, rel=0.15)
    assert result["R1"] + result["R2"] == pytest.approx(0.0020, rel=0.20)
    assert result["rmse_V"] < 0.001


def test_identify_fractional_synthetic(tmp_path: Path):
    sample = tmp_path / "sample_100cycle_fom.csv"
    _write_fractional_sample(sample)

    result = identify_fractional(sample)

    assert result["model"] == "FOM"
    assert result["R0"] == pytest.approx(0.0017, rel=0.15)
    assert result["alpha"] == pytest.approx(0.72, rel=0.20)
    assert result["rmse_V"] < 0.001


def test_run_ecm_identify_writes_params(tmp_path: Path):
    sample = tmp_path / "sample_100cycle_runner.csv"
    out_dir = tmp_path / "run"
    _write_fractional_sample(sample)

    result = run_ecm_identify("FOM", [str(sample)], out_dir)

    assert len(result) == 1
    assert (out_dir / "params_per_cycle.csv").exists()
    assert (out_dir / "REPORT.md").exists()
    assert (out_dir / "details" / f"{sample.stem}_fom.json").exists()


def test_sparse_low_cycle_is_flagged(tmp_path: Path):
    sample = tmp_path / "sample_sparse_100cycle.csv"
    _write_sparse_dcir_sample(sample)

    from algo.data_io import read_cycler_file

    df = read_cycler_file(str(sample))
    pre, pulse, post = _select_segments(df)
    quality = _segment_quality(pre, pulse, post)
    result = identify_fractional(sample)

    assert quality["fit_quality_flag"] == "insufficient_dynamic_samples"
    assert result["meta"]["fit_quality_flag"] == "insufficient_dynamic_samples"
    assert result["rmse_V"] is None
    assert result["alpha"] is None
