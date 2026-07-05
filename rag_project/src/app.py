from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))

from api import RagAPIClient
from components import render_metric_card, render_status_badge
from utils import get_asset_path, initialize_state, load_css, resolve_backend_url


def main() -> None:
    st.set_page_config(
        page_title="SmartDocs AI Pro",
        page_icon=get_asset_path("logo.png"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()
    initialize_state()

    st.logo(get_asset_path("logo.png"), icon_image=get_asset_path("logo.png"))

    backend_url = resolve_backend_url()
    client = RagAPIClient(backend_url)
    backend_status = client.health_check()
    st.session_state["backend_status"] = backend_status

    st.markdown(
        """
        <div class="hero-section">
            <div class="badge">SmartDocs AI Pro</div>
            <h1>Advanced document intelligence for grounded answers</h1>
            <p>Upload PDFs, HTML, or Markdown files, ask questions, and receive response with evidence-backed citations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Documents", str(len(st.session_state.get("documents", []))), "Uploaded assets")
    with col2:
        render_metric_card("Queries", str(len([m for m in st.session_state.get("chat_history", []) if m.get("role") == "assistant"])), "Interaction count")
    with col3:
        render_metric_card("Chunks", str(st.session_state.get("ingestion_summary", {}).get("chunks", 0)), "Indexed segments")
    with col4:
        render_metric_card("Backend", "Online" if backend_status.get("ok") else "Offline", "Connection status")

    st.markdown("<div class='section-title'>Launch a workflow</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Go to Upload Center", use_container_width=True):
            st.switch_page("pages/Upload.py")
    with c2:
        if st.button("Open Chat Workspace", use_container_width=True):
            st.switch_page("pages/Chat.py")
    with c3:
        if st.button("Inspect Analytics", use_container_width=True):
            st.switch_page("pages/Analytics.py")

    st.markdown("<div class='section-title'>Current system status</div>", unsafe_allow_html=True)
    status_col, details_col = st.columns([1, 2])
    with status_col:
        status_text = "Connected" if backend_status.get("ok") else "Waiting for backend"
        render_status_badge(status_text, success=backend_status.get("ok", False))
    with details_col:
        if backend_status.get("ok"):
            st.success("The Flask backend is reachable and ready for ingestion and chat requests.")
        else:
            st.warning("The backend is offline. Start the Flask service before uploading documents or chatting.")

    st.markdown("<div class='section-title'>Capabilities</div>", unsafe_allow_html=True)
    st.markdown(
        """
        - Upload multiple PDF, HTML, and Markdown files
        - Ingest them into the existing Flask backend
        - Ask grounded questions with source citations
        - Review analytics, cost estimates, and settings in one place
        """
    )


if __name__ == "__main__":
    main()
