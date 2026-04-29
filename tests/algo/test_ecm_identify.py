"""Tests for algo.ecm.ecm_identify."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from algo.ecm.ecm_identify import identify_1rc


def _fmt_time(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}.00"


def test_identify_1rc_synthetic():
    r0_true = 0.0020
    r1_true = 0.0015
    c1_true = 2000.0
    tau_true = r1_true * c1_true
    current_a = 10.0
    pulse_len = 10
    ocv = 3.700

    lines = ["StepNo,Voltage(V),Current(A),TotTime(H:M:S)"]
    total_time = 0
    for _ in range(5):
        lines.append(f"2,{ocv:.6f},0.0,{_fmt_time(total_time)}")
        total_time += 1

    for k in range(pulse_len):
        t = k + 1
        voltage = ocv - current_a * (r0_true + r1_true * (1.0 - np.exp(-t / tau_true)))
        lines.append(f"4,{voltage:.6f},{-current_a:.6f},{_fmt_time(total_time)}")
        total_time += 1

    amp_end = current_a * r1_true * (1.0 - np.exp(-pulse_len / tau_true))
    for k in range(8):
        t = k + 1
        voltage = ocv - amp_end * np.exp(-t / tau_true)
        lines.append(f"5,{voltage:.6f},0.0,{_fmt_time(total_time)}")
        total_time += 1

    sample = Path(tempfile.gettempdir()) / "codex_test_ecm_identify_synthetic.csv"
    try:
        sample.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = identify_1rc(sample)
        assert result["model"] == "1RC"
        assert result["R0"] == pytest.approx(r0_true, rel=0.20)
        assert result["R1"] == pytest.approx(r1_true, rel=0.35)
        assert result["C1"] == pytest.approx(c1_true, rel=0.55)
        assert result["rmse_V"] < 0.01
    finally:
        sample.unlink(missing_ok=True)
