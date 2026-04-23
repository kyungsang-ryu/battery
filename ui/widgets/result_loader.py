import json
import os
import pandas as pd
from typing import Iterator

def poll_progress(run_id: str, timeout_s: int = 600) -> Iterator[dict]:
    """outputs/runs/<run_id>/progress.json 파일을 mtime 변화 시 yield."""
    # TODO: 구현
    yield {}

def load_run(run_id: str) -> dict:
    """results.parquet, metrics.json, config.json 한 번에 로드."""
    # TODO: 구현
    return {}
