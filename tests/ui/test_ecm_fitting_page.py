import os
import pandas as pd
import pytest
from unittest.mock import patch
import importlib

@pytest.fixture
def mock_params_csv(tmp_path):
    # Create mock CSV
    df = pd.DataFrame({
        'model': ['FOM', 'FOM'],
        'cycle': [100, 1000],
        'temp_C': [25.0, 25.0],
        'R0': [0.001, 0.0005],
        'alpha': [None, 0.35],
        'rmse_V': [None, 0.0004],
        'fit_quality_flag': ['insufficient_dynamic_samples', 'ok']
    })
    csv_dir = tmp_path / "outputs" / "runs" / "K1-fom-25C"
    csv_dir.mkdir(parents=True, exist_ok=True)
    csv_path = csv_dir / "params_per_cycle.csv"
    df.to_csv(csv_path, index=False)
    return tmp_path

def test_ecm_fitting_page_render_mock(mock_params_csv, monkeypatch):
    # Change working directory to tmp_path
    monkeypatch.chdir(mock_params_csv)
    
    # Mock streamlit components to avoid real rendering
    with patch('streamlit.title'), patch('streamlit.header'), patch('streamlit.sidebar.radio', return_value="View K1 results"), patch('streamlit.plotly_chart') as mock_chart, patch('streamlit.subheader'):
        
        # Load the page module
        importlib.invalidate_caches()
        page = importlib.import_module("ui.pages.03_⚙️_ECM_Fitting")
        # importlib caches modules, so we need to reload it to run the top-level script again
        importlib.reload(page)
        
        # Ensure that make_ecm_param_trajectory and make_ecm_rmse_box didn't crash
        # and that plotly_chart was called
        assert mock_chart.called
