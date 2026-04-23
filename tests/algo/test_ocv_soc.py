"""Tests for algo.ocv.ocv_soc."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from algo.ocv.ocv_soc import compute_dqdv, extract_ocv_soc_from_rpt


def test_compute_dqdv_monotonic_discharge():
    time_s = np.arange(0, 3600, 1.0)
    current = -np.ones_like(time_s)
    voltage = 4.2 - (4.2 - 3.0) * (time_s / time_s[-1])
    df = compute_dqdv(voltage, current, time_s)
    assert {"V", "dQdV"}.issubset(df.columns)
    assert len(df) > 10
    assert df["dQdV"].dropna().abs().max() < 1e6
    assert df["dQdV"].dropna().size > 10


def test_extract_ocv_soc_from_rpt_synthetic():
    n = 3600
    df = pd.DataFrame(
        {
            "StepNo": np.ones(n, dtype=int),
            "Voltage(V)": np.linspace(4.15, 3.05, n),
            "Current(A)": np.full(n, -1.0),
            "TotTime(H:M:S)": [f"00:{m:02d}:{s:02d}.00" for m, s in ((i // 60, i % 60) for i in range(n))],
        }
    )
    sample = Path(tempfile.gettempdir()) / "codex_test_ocv_soc_synthetic.csv"
    try:
        df.to_csv(sample, index=False, encoding="utf-8")
        result = extract_ocv_soc_from_rpt(str(sample), nominal_capacity_ah=63.0)
        assert "error" not in result
        assert "discharge" in result
        discharge = result["discharge"]
        assert {"SOC", "OCV"}.issubset(discharge.columns)
        assert discharge["SOC"].min() >= 0
        assert discharge["SOC"].max() <= 100
    finally:
        sample.unlink(missing_ok=True)
