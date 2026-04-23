def test_ui_imports():
    import importlib
    
    from ui.data_analysis_ui import st
    
    p1 = importlib.import_module("ui.pages.01_📂_Data_Explorer")
    p2 = importlib.import_module("ui.pages.02_📈_OCV_dQdV")
    p3 = importlib.import_module("ui.pages.03_⚙️_ECM_Fitting")
    p4 = importlib.import_module("ui.pages.04_🔬_Estimator_Run")
    p5 = importlib.import_module("ui.pages.05_📊_Benchmark_View")
    
    assert st is not None
