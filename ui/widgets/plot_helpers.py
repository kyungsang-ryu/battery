import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
