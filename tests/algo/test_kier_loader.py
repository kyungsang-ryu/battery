"""Tests for algo.loaders.kier."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from algo.loaders.kier import list_kier_files, load_kier_run


def _make_local_tmp(prefix: str) -> Path:
    root = Path.cwd() / ".codex_test_tmp" / f"{prefix}_{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_list_kier_files_parses_three_datasets():
    root = _make_local_tmp("kier_catalog")
    try:
        main_root = root / "셀 엑셀파일" / "셀 엑셀파일"
        pouch_root = root / "02_실험_데이터" / "pouch_SOH"
        module_root = root / "모듈엑셀파일" / "모듈엑셀파일" / "모듈데이터 엑셀파일(2022.01~2023.07)"

        main_file = main_root / "CH2_25deg" / "RPT" / "22_09_26_에기연 열화셀_25deg_100cycle_RPT_ch2_M01Ch002(002).csv"
        main_file.parent.mkdir(parents=True, exist_ok=True)
        main_file.write_text(
            "StepNo,Voltage(V),Current(mA),TotTime(H:M:S)\n"
            "2,3.60,-100.0,00:00:00.00\n"
            "2,3.59,-100.0,00:00:01.00\n",
            encoding="utf-8",
        )

        pouch_file = (
            pouch_root
            / "pattern_MG_data"
            / "25도"
            / "MG_220418_MG_5_ch1_M01Ch008(008).csv"
        )
        pouch_file.parent.mkdir(parents=True, exist_ok=True)
        pouch_file.write_text(
            "StepNo,Voltage(V),Current(A),TotTime(Min)\n"
            "2,3.20,0.0,0.00\n"
            "2,3.21,0.0,0.50\n",
            encoding="utf-8",
        )
        ignored_step = (
            pouch_root
            / "pattern_MG_data"
            / "25도step"
            / "MG_220418_MG_5_ch1_M01Ch008(008)_step.csv"
        )
        ignored_step.parent.mkdir(parents=True, exist_ok=True)
        ignored_step.write_text("dummy\n", encoding="utf-8")

        pattern_dir = (
            module_root
            / "CH1"
            / "Pattern"
            / "2023_01_08_25deg_2000cycle"
        )
        base_file = pattern_dir / "2023_01_08_에기연_열화모듈_CYCLE_25deg_2000cycle_CH01.csv"
        chunk_0 = pattern_dir / "2023_01_08_에기연_열화모듈_CYCLE_25deg_2000cycle_CH01(0).csv"
        chunk_1 = pattern_dir / "2023_01_08_에기연_열화모듈_CYCLE_25deg_2000cycle_CH01(1).csv"
        for path, rows in (
            (
                base_file,
                [
                    "StepNo,Voltage(V),Current(A),TotTime",
                    "1,51.70,0.0,D0 00:00:00.10",
                    "1,51.69,0.0,D0 00:00:01.10",
                ],
            ),
            (
                chunk_0,
                [
                    "StepNo,Voltage(V),Current(A),TotTime",
                    "1,51.68,-5.0,D0 00:00:02.10",
                    "1,51.67,-5.0,D0 00:00:03.10",
                ],
            ),
            (
                chunk_1,
                [
                    "StepNo,Voltage(V),Current(A),TotTime",
                    "2,51.66,-5.0,D0 00:00:04.10",
                    "2,51.65,-5.0,D0 00:00:05.10",
                ],
            ),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")

        catalog = list_kier_files(
            roots={
                "main_cell": main_root,
                "pouch_soh": pouch_root,
                "module": module_root,
            }
        )
        assert len(catalog) == 3
        assert set(catalog["dataset"]) == {"main_cell", "pouch_soh", "module"}

        main_row = catalog[catalog["dataset"] == "main_cell"].iloc[0]
        assert main_row["cycle"] == 100
        assert main_row["type"] == "RPT"

        pouch_row = catalog[catalog["dataset"] == "pouch_soh"].iloc[0]
        assert pouch_row["weeks"] == 5
        assert pouch_row["type"] == "Pattern_MG"

        module_row = catalog[catalog["dataset"] == "module"].iloc[0]
        assert module_row["cycle"] == 2000
        assert module_row["type"] == "Pattern"
        assert len(module_row["pattern_chunks"]) == 3
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_load_kier_run_merges_module_pattern_chunks(monkeypatch):
    root = _make_local_tmp("kier_load")
    try:
        module_root = root / "모듈엑셀파일" / "모듈엑셀파일" / "모듈데이터 엑셀파일(2022.01~2023.07)"
        pattern_dir = module_root / "CH1" / "Pattern" / "2023_01_08_25deg_2000cycle"
        base_file = pattern_dir / "2023_01_08_에기연_열화모듈_CYCLE_25deg_2000cycle_CH01.csv"
        chunk_0 = pattern_dir / "2023_01_08_에기연_열화모듈_CYCLE_25deg_2000cycle_CH01(0).csv"
        chunk_1 = pattern_dir / "2023_01_08_에기연_열화모듈_CYCLE_25deg_2000cycle_CH01(1).csv"
        for path, rows in (
            (
                base_file,
                [
                    "StepNo,Voltage(V),Current(A),TotTime",
                    "1,51.70,0.0,D0 00:00:00.10",
                    "1,51.69,0.0,D0 00:00:01.10",
                ],
            ),
            (
                chunk_0,
                [
                    "StepNo,Voltage(V),Current(A),TotTime",
                    "1,51.68,-5.0,D0 00:00:02.10",
                    "1,51.67,-5.0,D0 00:00:03.10",
                ],
            ),
            (
                chunk_1,
                [
                    "StepNo,Voltage(V),Current(A),TotTime",
                    "2,51.66,-5.0,D0 00:00:04.10",
                    "2,51.65,-5.0,D0 00:00:05.10",
                ],
            ),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")

        monkeypatch.setattr(
            "algo.loaders.kier.SCAN_ROOTS",
            {
                "main_cell": root / "셀 엑셀파일" / "셀 엑셀파일",
                "pouch_soh": root / "02_실험_데이터" / "pouch_SOH",
                "module": module_root,
            },
        )
        loaded = load_kier_run(str(base_file))
        df = loaded["df"]
        assert len(df) == 6
        assert df["time_s"].is_monotonic_increasing
        assert loaded["meta"]["n_chunks"] == 3
        assert loaded["meta"]["schema_variant"] == "module_days_hms"
    finally:
        shutil.rmtree(root, ignore_errors=True)
