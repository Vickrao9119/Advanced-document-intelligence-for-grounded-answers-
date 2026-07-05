from __future__ import annotations

import streamlit as st

from components import render_metric_card, render_status_badge
from utils import initialize_state, load_css, resolve_backend_url


st.set_page_config(page_title="Home", layout="wide")
load_css()
initialize_state()

st.markdown("# Home")
st.markdown("SmartDocs AI Pro gives you a polished workspace for grounded answer generation and document intelligence.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Documents", str(len(st.session_state.get("documents", []))), "Uploaded assets")
with col2:
    render_metric_card("Queries", str(len([m for m in st.session_state.get("chat_history", []) if m.get("role") == "assistant"])), "Conversation turns")
with col3:
    render_metric_card("Chunks", str(st.session_state.get("ingestion_summary", {}).get("chunks", 0)), "Indexed segments")
with col4:
    render_metric_card("Backend", "Online" if st.session_state.get("backend_status", {}).get("ok") else "Offline", "Connection status")

st.markdown("## System status")
status_col, info_col = st.columns([1, 3])
with status_col:
    render_status_badge("Connected" if st.session_state.get("backend_status", {}).get("ok") else "Offline", success=st.session_state.get("backend_status", {}).get("ok", False))
with info_col:
    st.info(f"Backend URL: {resolve_backend_url()}")
