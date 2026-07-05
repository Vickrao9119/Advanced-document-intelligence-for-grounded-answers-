from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent


def get_asset_path(filename: str) -> str:
    return str(SRC_DIR / "assets" / filename)


def load_css() -> None:
    css_path = SRC_DIR / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def initialize_state() -> None:
    defaults = {
        "backend_url": os.getenv("RAG_BACKEND_URL", "http://127.0.0.1:8000"),
        "chat_history": [],
        "documents": [],
        "ingestion_summary": {},
        "backend_status": {},
        "settings": {
            "chunk_size": 600,
            "overlap": 120,
            "top_k": 5,
            "temperature": 0.2,
            "embedding_model": "Offline TF-IDF",
        },
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def resolve_backend_url() -> str:
    initialize_state()
    return str(st.session_state.get("backend_url", os.getenv("RAG_BACKEND_URL", "http://127.0.0.1:8000")))


def sanitize_filename(name: str) -> str:
    stem = Path(name).stem
    suffix = Path(name).suffix.lower()
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in stem)
    return f"{safe or 'upload'}{suffix}"


def save_uploaded_files(uploaded_files: list[Any], target_dir: str) -> list[str]:
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    saved_paths: list[str] = []
    for uploaded_file in uploaded_files:
        destination = Path(target_dir) / sanitize_filename(uploaded_file.name)
        with destination.open("wb") as handle:
            handle.write(uploaded_file.getbuffer())
        saved_paths.append(str(destination))
    return saved_paths
