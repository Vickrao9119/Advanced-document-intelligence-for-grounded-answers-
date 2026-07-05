from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from api import RagAPIClient
from components import render_metric_card, render_status_badge
from utils import initialize_state, load_css, resolve_backend_url, save_uploaded_files


st.set_page_config(page_title="Upload", layout="wide")
load_css()
initialize_state()

client = RagAPIClient(resolve_backend_url())

st.markdown("# Upload Documents")
st.markdown("Upload PDF, HTML, or Markdown files and ingest them into the Flask backend.")

uploaded_files = st.file_uploader("Choose files", type=["pdf", "html", "md", "markdown", "txt"], accept_multiple_files=True)

if uploaded_files:
    target_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads")
    target_dir = os.path.abspath(target_dir)
    saved_paths = save_uploaded_files(list(uploaded_files), target_dir)
    st.session_state["documents"] = saved_paths
    progress = st.progress(0)
    for index, path in enumerate(saved_paths, start=1):
        progress.progress(index / len(saved_paths))
    st.success(f"Saved {len(saved_paths)} file(s) to disk.")

    if st.button("Run ingestion"):
        with st.spinner("Ingesting files into the backend..."):
            result = client.ingest_documents(os.path.dirname(saved_paths[0]))
            st.session_state["ingestion_summary"] = result
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(f"Ingested {result.get('chunks', 0)} chunks from {result.get('documents_ingested', 0)} document(s).")

col1, col2, col3 = st.columns(3)
with col1:
    render_metric_card("Pending Files", str(len(uploaded_files or [])), "Selected for upload")
with col2:
    render_metric_card("Saved Files", str(len(st.session_state.get("documents", []))), "Files available locally")
with col3:
    render_metric_card("Ingestion", str(st.session_state.get("ingestion_summary", {}).get("chunks", 0)), "Indexed chunks")
