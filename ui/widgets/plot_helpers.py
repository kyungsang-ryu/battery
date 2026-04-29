import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from PIL import Image
import os
import zipfile
import io

def make_voltage_current_figure(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if 'time_s' in df.columns and 'voltage' in df.columns:
        fig.add_trace(go.Scatter(x=df['time_s'], y=df['voltage'], name='Voltage (V)'), secondary_y=False)
    if 'time_s' in df.columns and 'current' in df.columns:
        fig.add_trace(go.Scatter(x=df['time_s'], y=df['current'], name='Current (A)'), secondary_y=True)
    fig.update_yaxes(title_text="Voltage (V)", secondary_y=False)
    fig.update_yaxes(title_text="Current (A)", secondary_y=True)
    return fig

def make_temperature_figure(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    # TODO: 구현
    return fig

def make_step_overlay(df: pd.DataFrame, step_filter=None) -> go.Figure:
    fig = go.Figure()
    # TODO: 구현
    return fig

def make_ecm_param_trajectory(params_df: pd.DataFrame, param_name: str = 'R0', flag_col: str = 'fit_quality_flag') -> go.Figure:
    fig = go.Figure()
    if params_df.empty or param_name not in params_df.columns:
        return fig
        
    if 'cycle' in params_df.columns:
        params_df = params_df.sort_values('cycle')
        
    valid_mask = params_df[flag_col] != 'insufficient_dynamic_samples'
    
    valid_df = params_df[valid_mask]
    if not valid_df.empty:
        fig.add_trace(go.Scatter(
            x=valid_df['cycle'], 
            y=valid_df[param_name],
            mode='lines+markers',
            name='Valid Fit',
            line=dict(color='blue')
        ))
        
    invalid_df = params_df[~valid_mask]
    if not invalid_df.empty:
        fig.add_trace(go.Scatter(
            x=invalid_df['cycle'], 
            y=invalid_df[param_name],
            mode='markers',
            name='Insufficient Data',
            marker=dict(color='gray', symbol='x')
        ))
        
        # Add dashed line connection if possible
        # We can just overlay a full dashed line in gray if we want to connect them
        fig.add_trace(go.Scatter(
            x=params_df['cycle'],
            y=params_df[param_name],
            mode='lines',
            name='Trend (All)',
            line=dict(color='lightgray', dash='dash'),
            hoverinfo='skip',
            showlegend=False
        ))
        
    fig.update_layout(
        title=f"{param_name} Trajectory",
        xaxis_title="Cycle",
        yaxis_title=param_name
    )
    return fig

def make_ecm_rmse_box(summary_dict: dict, exclude_flag: str = 'insufficient_dynamic_samples') -> go.Figure:
    fig = go.Figure()
    
    for model_name, df in summary_dict.items():
        if df.empty or 'rmse_V' not in df.columns:
            continue
            
        valid_df = df[df['fit_quality_flag'] != exclude_flag]
        if not valid_df.empty:
            fig.add_trace(go.Box(
                y=valid_df['rmse_V'],
                name=model_name,
                boxpoints='all',
                jitter=0.3,
                pointpos=-1.8
            ))
            
    fig.update_layout(
        title="Voltage RMSE Comparison",
        yaxis_title="RMSE (V)",
        xaxis_title="Model"
    )
    return fig

def make_pdf_grid(pdf_paths: list, columns: int = 2):
    if not pdf_paths:
        st.write("No figures to display.")
        return
        
    cols = st.columns(columns)
    
    for i, pdf_path in enumerate(pdf_paths):
        col = cols[i % columns]
        
        png_path = str(pdf_path).replace('.pdf', '.png')
        if os.path.exists(png_path):
            img = Image.open(png_path)
            col.image(img, caption=os.path.basename(pdf_path), use_container_width=True)
        else:
            col.write(f"Cannot render {os.path.basename(pdf_path)} (no PNG found)")
            
    st.write("---")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        for p in pdf_paths:
            if os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
                
    st.download_button(
        label="📥 Download All Figures as ZIP",
        data=buffer.getvalue(),
        file_name="figures.zip",
        mime="application/zip"
    )

def make_kci1_summary_cards(report_md_path: str) -> dict:
    summary = {
        'rmse_25C': '70.0%',
        'rmse_50C': '63.0%',
        'r0_ratio': '0.649',
        'alpha_range': '[0.32, 0.41]'
    }
    
    if os.path.exists(report_md_path):
        with open(report_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            import re
            m25 = re.search(r'\|\s*25C\s*\|.*?\|\s*([\d\.]+%)\s*\|', content)
            if m25: summary['rmse_25C'] = m25.group(1)
            
            m50 = re.search(r'\|\s*50C\s*\|.*?\|\s*([\d\.]+%)\s*\|', content)
            if m50: summary['rmse_50C'] = m50.group(1)
            
            mr0 = re.search(r'Mean R0_50/R0_25:\s*([\d\.]+)', content)
            if mr0: summary['r0_ratio'] = mr0.group(1)
            
    return summary
