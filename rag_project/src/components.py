from __future__ import annotations

from typing import Any

import streamlit as st


def render_sidebar_navigation() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-icon">✨</div>
                <div>
                    <div class="brand-title">SmartDocs AI Pro</div>
                    <div class="brand-subtitle">Offline-ready RAG workspace</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/Home.py", label="Home", icon="🏠")
        st.page_link("pages/Upload.py", label="Upload", icon="📤")
        st.page_link("pages/Chat.py", label="Chat", icon="💬")
        st.page_link("pages/Analytics.py", label="Analytics", icon="📊")
        st.page_link("pages/Cost_Analysis.py", label="Cost Analysis", icon="💰")
        st.page_link("pages/Settings.py", label="Settings", icon="⚙️")
        st.markdown("<div class='sidebar-footer'>Backend integration is active through the Flask endpoints.</div>", unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(label: str, success: bool = True) -> None:
    color = "#2dd4bf" if success else "#fb923c"
    st.markdown(
        f"""
        <div class="status-badge" style="border-color:{color}; color:{color};">{label}</div>
        """,
        unsafe_allow_html=True,
    )


def render_citation_cards(citations: list[dict[str, Any]]) -> None:
    if not citations:
        return
    st.markdown("<div class='section-title'>Source citations</div>", unsafe_allow_html=True)
    for citation in citations:
        st.markdown(
            f"""
            <div class="citation-card">
                <div class="citation-title">{citation.get('document', 'Source')}</div>
                <div class="citation-meta">Chunk {citation.get('chunk_id', 'n/a')}</div>
                <div class="citation-path">{citation.get('source_path', 'Unknown source')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
