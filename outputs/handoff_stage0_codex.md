# Stage 0 Handoff

1. [변경 요약]: T1~T7에서 `algo/` 구조 마이그레이션, OCV/dQdV, chemistry check, 1-RC ECM, KIER loader/catalog를 완료했고, 이번 마감에서는 인벤토리 보고서 두 파일을 canonical path와 `outputs/catalog_kier_v0.csv` 기준으로 정정했다.
2. [공개 API 영향]: 분업 Spec §3 기존 시그니처 변경은 없고, Stage 0에서 추가된 공개 함수는 `algo.ecm.ecm_identify.identify_1rc`, `identify_2rc`, `algo.loaders.kier.list_kier_files`, `load_kier_run`, `merge_pattern_chunks`, `dump_catalog_artifacts` 이다.
3. [pytest 결과]:
```text
...........                                                              [100%]
11 passed in 1.23s
```
4. [Antigravity에 알릴 것]: 새로 import 가능한 함수는 `compute_dqdv`, `extract_ocv_soc_from_rpt`, `classify_chemistry`, `identify_1rc`, `identify_2rc`, `list_kier_files`, `load_kier_run`, `merge_pattern_chunks`, `dump_catalog_artifacts` 이고, 새 산출물은 `outputs/ocv_soc/*`, `outputs/ecm/1rc_25C_cycle1300_v0.json`, `outputs/catalog_kier_v0.csv`, `outputs/catalog_summary_v0.md`, `outputs/recon_2026-04-23.md`, `outputs/handoff_stage0_codex.md` 이다.
