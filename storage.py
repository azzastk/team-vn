"""
Module quản lý "kho dữ liệu" kết quả chấm điểm.

- Luôn lưu 1 bản CSV local tại data/results.csv (dùng để xem/tải ngay trong app).
- Nếu Space có cấu hình 2 Secret: HF_TOKEN và HF_DATASET_REPO,
  mỗi lần có kết quả mới app sẽ tự đồng bộ (upload) toàn bộ CSV lên
  một Dataset repo trên Hugging Face -> dữ liệu KHÔNG bị mất khi Space
  bị restart/sleep (khác với ổ đĩa local của Space là tạm thời).
"""

import os
import io
import datetime
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH = os.path.join(DATA_DIR, "results.csv")


def _get_secret(name):
    """Đọc biến cấu hình từ env var trước (Hugging Face Spaces),
    nếu không có thì thử st.secrets (Streamlit Community Cloud)."""
    val = os.environ.get(name)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None


HF_TOKEN = _get_secret("HF_TOKEN")
HF_DATASET_REPO = _get_secret("HF_DATASET_REPO")  # vd: "ten-user/nst-scoring-results"


def _ensure_local_file(columns):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=columns).to_csv(CSV_PATH, index=False)


def append_record(record: dict):
    """Thêm 1 dòng kết quả mới vào kho dữ liệu (local + Hugging Face nếu có cấu hình)."""
    columns = list(record.keys())
    _ensure_local_file(columns)

    df = pd.read_csv(CSV_PATH) if os.path.getsize(CSV_PATH) > 0 else pd.DataFrame(columns=columns)
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

    synced_to_hub = False
    error = None
    if HF_TOKEN and HF_DATASET_REPO:
        try:
            _sync_to_hf_dataset(df)
            synced_to_hub = True
        except Exception as e:  # không để lỗi mạng làm crash app
            error = str(e)

    return df, synced_to_hub, error


def _sync_to_hf_dataset(df: pd.DataFrame):
    from huggingface_hub import HfApi

    api = HfApi(token=HF_TOKEN)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    api.upload_file(
        path_or_fileobj=buffer,
        path_in_repo="results.csv",
        repo_id=HF_DATASET_REPO,
        repo_type="dataset",
    )


def load_all() -> pd.DataFrame:
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame()


def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
