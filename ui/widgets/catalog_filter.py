import streamlit as st
import pandas as pd

def render_catalog_filter(catalog: pd.DataFrame) -> pd.DataFrame:
    """사이드바에 필터 위젯을 렌더하고, 필터링된 catalog를 반환."""
    st.sidebar.subheader("데이터 필터")
    if catalog is None or catalog.empty:
        st.sidebar.warning("로딩된 카탈로그가 없습니다.")
        return catalog
        
    df = catalog.copy()
    
    # 1. Dataset 필터
    datasets = ['main_cell', 'pouch_soh', 'module']
    selected_datasets = st.sidebar.multiselect("Dataset", options=datasets, default=datasets)
    if selected_datasets:
        df = df[df['dataset'].isin(selected_datasets)]
        
    # 2. Channel 필터 (동적)
    channels = df['channel'].unique().tolist()
    selected_channels = st.sidebar.multiselect("Channel", options=channels, default=channels)
    if selected_channels:
        df = df[df['channel'].isin(selected_channels)]
        
    # 3. Temp_C 필터 (0, 25, 40, 50 - 40은 pouch_soh 전용이지만 데이터 유무에 따라 필터)
    temps = [0, 25, 40, 50]
    selected_temps = st.sidebar.multiselect("Temperature (°C)", options=temps, default=temps)
    if selected_temps:
        df = df[df['temp_C'].isin(selected_temps)]
        
    # 4. Type 필터
    types = ['RPT', 'DCIR', 'DCIR후충전', 'ACIR', 'Pattern', 'Pattern_MG', 'Pattern_PVSmoothing', 'Pattern_PowerQuality', 'capacity_check']
    selected_types = st.sidebar.multiselect("Test Type", options=types, default=[])
    if selected_types:
        df = df[df['type'].isin(selected_types)]
        
    # 5. Cycle / Weeks 토글식 슬라이더 (Dataset에 종속적)
    if set(selected_datasets) == {'pouch_soh'} and 'weeks' in df.columns:
        # Pouch_SOH 선택 시 주 단위
        min_w, max_w = 5, 30
        selected_weeks = st.sidebar.slider("Weeks Range", min_value=min_w, max_value=max_w, value=(min_w, max_w))
        df = df[(df['weeks'].isna()) | ((df['weeks'] >= selected_weeks[0]) & (df['weeks'] <= selected_weeks[1]))]
    else:
        # 그 외에는 Cycle 단위
        if 'cycle' in df.columns and not df['cycle'].isna().all():
            min_c = int(df['cycle'].min(skipna=True))
            max_c = int(df['cycle'].max(skipna=True))
            if max_c > min_c:
                selected_cycles = st.sidebar.slider("Cycle Range", min_value=min_c, max_value=max_c, value=(min_c, max_c))
                df = df[(df['cycle'].isna()) | ((df['cycle'] >= selected_cycles[0]) & (df['cycle'] <= selected_cycles[1]))]
                
    st.sidebar.text(f"필터 결과: {len(df)}건")
    return df
