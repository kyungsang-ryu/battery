import streamlit as st
import pandas as pd
import os
import glob
from ui.widgets.plot_helpers import make_ecm_param_trajectory, make_ecm_rmse_box, make_pdf_grid
from algo.ecm.ecm_identify import identify_1rc
from algo.ecm.ecm_2rc import identify_2rc
from algo.ecm.fractional_ecm import identify_fractional

st.title("⚙️ ECM Fitting")

# Sidebar Toggle
mode = st.sidebar.radio("Mode", ["Identify new", "View K1 results"])

if mode == "Identify new":
    st.header("Identify new")
    st.write("새 데이터에 대한 ECM 식별을 수행합니다.")
    
    model_choice = st.radio("Model Selection", ["1-RC", "2-RC", "Fractional (FOM)", "Compare All"])
    
    # Placeholder for the new identify logic
    # The user says "알고리즘 로직 (분수계 식, 회귀) 을 UI 에 작성 금지"
    # So we just provide the structure
    st.write("식별 기능을 위해 데이터를 로드하세요.")
    
    # Assume we have some results (Mock for now, since we just need the UI structure)
    # The actual integration would depend on user inputs like file upload, which is not fully specified yet.
    # The prompt mainly emphasizes integrating KCI1 outputs.

elif mode == "View K1 results":
    st.header("View K1 results")
    
    runs_dir = os.path.join("outputs", "runs")
    
    # Load data
    summary_dict = {}
    models_to_load = {
        "1-RC": ["K1-1rc-25C", "K1-1rc-50C"],
        "2-RC": ["K1-2rc-25C", "K1-2rc-50C"],
        "Fractional (FOM)": ["K1-fom-25C", "K1-fom-50C"]
    }
    
    for model_name, folders in models_to_load.items():
        dfs = []
        for folder in folders:
            csv_path = os.path.join(runs_dir, folder, "params_per_cycle.csv")
            if os.path.exists(csv_path):
                dfs.append(pd.read_csv(csv_path))
        if dfs:
            summary_dict[model_name] = pd.concat(dfs, ignore_index=True)
            
    if not summary_dict:
        st.warning("K1 결과 데이터가 없습니다. 먼저 분석을 실행하세요.")
    else:
        # Trajectories
        st.subheader("Parameter Trajectories")
        param_to_plot = st.selectbox("Select Parameter", ["R0", "alpha", "rmse_V", "R1", "C1"])
        
        # We plot trajectory for each model
        for model_name, df in summary_dict.items():
            if param_to_plot in df.columns:
                st.write(f"**{model_name}**")
                fig = make_ecm_param_trajectory(df, param_name=param_to_plot)
                st.plotly_chart(fig, use_container_width=True)
                
        # RMSE Boxplot
        st.subheader("Voltage RMSE Comparison")
        box_fig = make_ecm_rmse_box(summary_dict)
        st.plotly_chart(box_fig, use_container_width=True)
        
        # Figure Grid
        st.subheader("Pre-computed Figures")
        fig_dir = os.path.join("outputs", "figures", "K1_fractional_ecm")
        if os.path.exists(fig_dir):
            pdf_paths = glob.glob(os.path.join(fig_dir, "fig*.pdf"))
            # Sort naturally
            pdf_paths = sorted(pdf_paths)
            make_pdf_grid(pdf_paths, columns=2)
        else:
            st.info("No pre-computed figures found in outputs/figures/K1_fractional_ecm")

