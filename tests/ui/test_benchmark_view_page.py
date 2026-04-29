import os
import pandas as pd
import pytest
from unittest.mock import patch
import importlib

@pytest.fixture
def mock_outputs(tmp_path):
    # Create mock CSV
    df = pd.DataFrame({
        'model': ['FOM', 'FOM'],
        'cycle': [100, 1000],
        'temp_label': ['25C', '25C'],
        'R0': [0.001, 0.0005],
        'alpha': [None, 0.35],
        'rmse_V': [None, 0.0004],
        'fit_quality_flag': ['insufficient_dynamic_samples', 'ok']
    })
    
    csv_dir = tmp_path / "outputs" / "runs" / "K1-fom-25C"
    csv_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_dir / "params_per_cycle.csv", index=False)
    
    # Create mock report
    summary_dir = tmp_path / "outputs" / "runs" / "K1-summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    
    with open(summary_dir / "REPORT.md", "w", encoding="utf-8") as f:
        f.write("| 25C | 1RC | 2RC | FOM | 70.0% |\n| 50C | 1RC | 2RC | FOM | 63.0% |\nMean R0_50/R0_25: 0.649\n")
        
    with open(summary_dir / "diagnosis_low_cycle.md", "w", encoding="utf-8") as f:
        f.write("Diagnosis mock")
        
    return tmp_path

def test_benchmark_view_page_render(mock_outputs, monkeypatch):
    monkeypatch.chdir(mock_outputs)
    
    with patch('streamlit.title'), patch('streamlit.header'), patch('streamlit.selectbox', return_value="KCI1 (분수계 ECM)"), \
         patch('streamlit.plotly_chart'), patch('streamlit.dataframe'), patch('streamlit.markdown'), \
         patch('streamlit.columns') as mock_cols:
         
         # Mock columns
         from unittest.mock import MagicMock
         mock_col = MagicMock()
         mock_cols.return_value = [mock_col, mock_col, mock_col, mock_col]
         
         importlib.invalidate_caches()
         page = importlib.import_module("ui.pages.05_📊_Benchmark_View")
         importlib.reload(page)
         
         assert mock_col.metric.called
