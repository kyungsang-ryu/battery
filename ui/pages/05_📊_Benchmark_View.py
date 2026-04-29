import streamlit as st
import pandas as pd
import os
import glob
from ui.widgets.plot_helpers import make_ecm_param_trajectory, make_pdf_grid, make_kci1_summary_cards

st.title("📊 Benchmark View")

sheet = st.selectbox("Sheet Selection", [
    "KCI1 (분수계 ECM)",
    "KCI2 (Placeholder)",
    "SCI1 (Placeholder)",
    "SCI2 (Placeholder)",
    "SCI3 (Placeholder)"
])

if sheet != "KCI1 (분수계 ECM)":
    st.write(f"**{sheet}** 준비 중입니다.")
    st.stop()

st.header("KCI1: Fractional ECM Benchmark")

runs_dir = os.path.join("outputs", "runs")
summary_dir = os.path.join(runs_dir, "K1-summary")
report_path = os.path.join(summary_dir, "REPORT.md")

summary = make_kci1_summary_cards(report_path)

col1, col2, col3, col4 = st.columns(4)
col1.metric("RMSE 25°C Reduction", summary.get('rmse_25C', 'N/A'))
col2.metric("RMSE 50°C Reduction", summary.get('rmse_50C', 'N/A'))
col3.metric("R0_50 / R0_25", summary.get('r0_ratio', 'N/A'))
col4.metric("Alpha Range", summary.get('alpha_range', 'N/A'))

st.info("""
**Main Claims:**
- Fractional ECM cuts voltage RMSE by 70% (25°C) and 63% (50°C) vs 1-RC
- R0_50°C / R0_25°C = 0.649 — temperature dependency confirmed
- α stable in [0.32, 0.41] — fit reliability of fractional model
""")

summary_dict = {}
models_to_load = {
    "1-RC": ["K1-1rc-25C", "K1-1rc-50C"],
    "2-RC": ["K1-2rc-25C", "K1-2rc-50C"],
    "FOM": ["K1-fom-25C", "K1-fom-50C"]
}

for model_name, folders in models_to_load.items():
    dfs = []
    for folder in folders:
        csv_path = os.path.join(runs_dir, folder, "params_per_cycle.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            temp = "25C" if "25C" in folder else "50C"
            df['temp_label'] = temp
            dfs.append(df)
    if dfs:
        summary_dict[model_name] = pd.concat(dfs, ignore_index=True)

st.subheader("Section 1: Mean Voltage RMSE Comparison")
if summary_dict:
    rmse_records = []
    for model_name, df in summary_dict.items():
        valid_df = df[df['fit_quality_flag'] != 'insufficient_dynamic_samples']
        mean_25c = valid_df[valid_df['temp_label'] == '25C']['rmse_V'].mean()
        mean_50c = valid_df[valid_df['temp_label'] == '50C']['rmse_V'].mean()
        rmse_records.append({"Model": model_name, "25C RMSE (V)": mean_25c, "50C RMSE (V)": mean_50c})
        
    rmse_df = pd.DataFrame(rmse_records)
    st.dataframe(rmse_df, use_container_width=True)
else:
    st.warning("Data not found.")

st.subheader("Section 2: R0 & α Trajectories")
if summary_dict:
    st.markdown("**(insufficient flag cycle 은 회색 점선 표시됨)**")
    
    tab1, tab2 = st.tabs(["R0 Trajectory", "α Trajectory (FOM Only)"])
    
    with tab1:
        for model_name, df in summary_dict.items():
            for temp_label in ["25C", "50C"]:
                sub_df = df[df['temp_label'] == temp_label]
                if not sub_df.empty:
                    st.write(f"**{model_name} - {temp_label}**")
                    st.plotly_chart(make_ecm_param_trajectory(sub_df, param_name='R0'), use_container_width=True)
                    
    with tab2:
        if "FOM" in summary_dict:
            df_fom = summary_dict["FOM"]
            for temp_label in ["25C", "50C"]:
                sub_df = df_fom[df_fom['temp_label'] == temp_label]
                if not sub_df.empty:
                    st.write(f"**FOM - {temp_label}**")
                    st.plotly_chart(make_ecm_param_trajectory(sub_df, param_name='alpha'), use_container_width=True)

st.subheader("Section 3: Fractional ECM Figures")
fig_dir = os.path.join("outputs", "figures", "K1_fractional_ecm")
if os.path.exists(fig_dir):
    pdf_paths = sorted(glob.glob(os.path.join(fig_dir, "fig*.pdf")))
    make_pdf_grid(pdf_paths, columns=2)
else:
    st.info("No figures found.")

st.subheader("Section 4: Low-cycle Anomaly Diagnosis")
diag_md_path = os.path.join(summary_dir, "diagnosis_low_cycle.md")
if os.path.exists(diag_md_path):
    with open(diag_md_path, 'r', encoding='utf-8') as f:
        st.markdown(f.read())
        
diag_pdfs = sorted(glob.glob(os.path.join(summary_dir, "diagnosis_*.pdf")))
if diag_pdfs:
    make_pdf_grid(diag_pdfs, columns=2)

st.info("왜 cycle 100/500 이 fit 불가능한가: 위 리포트와 같이 1초 남짓의 짧은 펄스 기록만 있어서 분수계/다중-RC 식별에 필요한 충분한 동특성 구간을 얻을 수 없기 때문입니다.")

st.subheader("Section 5: K1 Fractional ECM Full Report")
if os.path.exists(report_path):
    with open(report_path, 'r', encoding='utf-8') as f:
        st.markdown(f.read())
