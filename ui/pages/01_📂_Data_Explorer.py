import streamlit as st
import pandas as pd
import numpy as np

# Codex import 시도 (P0.5 의존성)
try:
    from algo.loaders.kier import list_kier_files, load_kier_run
    HAS_ALGO = True
except ImportError:
    HAS_ALGO = False

from ui.widgets.catalog_filter import render_catalog_filter
from ui.widgets.plot_helpers import make_voltage_current_figure

st.title("📂 Data Explorer")

# 1. 카탈로그 로드
@st.cache_data
def get_catalog():
    if HAS_ALGO:
        return list_kier_files()
    else:
        # Placeholder Catalog
        st.warning("algo.loaders.kier 모듈이 없습니다. Placeholder 데이터를 사용합니다.")
        return pd.DataFrame({
            "file_path": ["dummy1.csv", "dummy2.csv"],
            "dataset": ["main_cell", "pouch_soh"],
            "channel": ["ch2", "ch1"],
            "temp_C": [25, 40],
            "type": ["RPT", "Pattern"],
            "cycle": [100, None],
            "weeks": [None, 10],
            "n_chunks": [1, 1]
        })

catalog = get_catalog()

# 2. 상단: 갱신 버튼 & 통계 카드
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🔄 카탈로그 갱신"):
        st.cache_data.clear()
        st.rerun()

with col2:
    if not catalog.empty:
        st.info(f"총 {len(catalog)}개의 데이터 로드 완료. (Dataset: {catalog['dataset'].nunique()}종, Temp: {catalog['temp_C'].nunique()}종)")

# 3. 사이드바 필터 적용
filtered_catalog = render_catalog_filter(catalog)

# 4. 본문: 데이터프레임과 선택 결과
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("데이터 파일 목록")
    st.dataframe(filtered_catalog, use_container_width=True)

with col_right:
    st.subheader("시계열 뷰어")
    # 파일명 선택을 위한 UI (테이블에서 직접 선택은 st.data_editor 등 필요하므로 selbox 대체)
    if not filtered_catalog.empty:
        selected_file = st.selectbox("파일을 선택하세요", filtered_catalog["file_path"].tolist())
        
        if selected_file:
            st.write(f"선택: **{selected_file}**")
            
            # TODO: 다운로드 버튼
            st.download_button("다운로드 (CSV)", data="dummy data", file_name="data.csv", mime="text/csv")
            
            # 파일 시각화
            if HAS_ALGO:
                # Codex load_kier_run 호출
                try:
                    run_data = load_kier_run(selected_file, merge_chunks=True)
                    fig = make_voltage_current_figure(run_data["df"])
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"데이터 로드 중 오류 발생: {e}")
            else:
                st.info("알고리즘 연동 대기 중입니다. 차트가 표시되지 않습니다.")
    else:
        st.write("표시할 데이터가 없습니다.")
