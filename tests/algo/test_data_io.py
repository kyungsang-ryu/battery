"""Tests for algo.data_io."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from algo.data_io import (
    _parse_hms_time,
    detect_format,
    normalize_columns,
    read_cycler_file,
)


def test_detect_format_by_extension():
    assert detect_format("foo/bar.txt") == "txt"
    assert detect_format("x/y.csv") == "csv"
    assert detect_format("a.XLSX") == "xlsx"
    assert detect_format("no_ext") == "unknown"


def test_parse_hms_time():
    assert _parse_hms_time(" 00:00:01.50") == pytest.approx(1.5)
    assert _parse_hms_time("01:00:00.00") == pytest.approx(3600.0)
    assert _parse_hms_time(" 00:01:30.00") == pytest.approx(90.0)
    assert _parse_hms_time("nan") != _parse_hms_time("nan")


def test_normalize_columns_standardizes_aliases():
    df = pd.DataFrame(
        {
            "StepNo": [1, 2],
            "Voltage(V)": [3.6, 3.7],
            "Current(mA)": [-100.0, -100.0],
            "TotTime(H:M:S)": ["00:00:00.00", "00:00:01.00"],
        }
    )
    out, ma_mapped, hms_mapped = normalize_columns(df)
    assert {"step", "voltage", "current", "time_s"}.issubset(out.columns)
    assert "current" in ma_mapped
    assert "time_s" in hms_mapped
    assert out["voltage"].iloc[0] == 3.6


def test_read_cycler_file_pne_style():
    content = (
        "StepNo,Voltage(V),Current(mA),TotTime(H:M:S)\n"
        "2,3.60,-100.0, 00:00:00.00\n"
        "2,3.59,-100.0, 00:00:01.00\n"
    )
    sample = Path(tempfile.gettempdir()) / "codex_test_read_cycler_file_sample.csv"
    try:
        sample.write_text(content, encoding="cp949")
        df = read_cycler_file(str(sample))
        assert list(df.columns[:4]) == ["step", "voltage", "current", "time_s"]
        assert len(df) == 2
        assert df["voltage"].iloc[1] == pytest.approx(3.59)
        assert df["current"].iloc[0] == pytest.approx(-0.1)
        assert df["time_s"].iloc[1] == pytest.approx(1.0)
    finally:
        sample.unlink(missing_ok=True)


def test_read_cycler_file_module_day_time():
    content = (
        "StepNo,Voltage(V),Current(A),TotTime,OvenTemperature(`C)\n"
        "2,51.70,0.0,D0 00:00:00.10,25.0\n"
        "2,51.69,0.0,D0 00:00:01.10,25.1\n"
    )
    sample = Path(tempfile.gettempdir()) / "codex_test_read_cycler_module.csv"
    try:
        sample.write_text(content, encoding="utf-8")
        df = read_cycler_file(str(sample))
        assert df["time_s"].iloc[0] == pytest.approx(0.1)
        assert df["time_s"].iloc[1] == pytest.approx(1.1)
        assert df["current"].iloc[1] == pytest.approx(0.0)
        assert df["temperature"].iloc[1] == pytest.approx(25.1)
    finally:
        sample.unlink(missing_ok=True)


def test_read_cycler_file_minute_time():
    content = (
        "StepNo,Voltage(V),Current(A),TotTime(Min)\n"
        "2,3.60,-1.0,0.00\n"
        "2,3.59,-1.0,0.50\n"
    )
    sample = Path(tempfile.gettempdir()) / "codex_test_read_cycler_minutes.csv"
    try:
        sample.write_text(content, encoding="utf-8")
        df = read_cycler_file(str(sample))
        assert df["time_s"].iloc[0] == pytest.approx(0.0)
        assert df["time_s"].iloc[1] == pytest.approx(30.0)
        assert df["current"].iloc[0] == pytest.approx(-1.0)
    finally:
        sample.unlink(missing_ok=True)
