from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from components import render_metric_card
from utils import initialize_state, load_css


st.set_page_config(page_title="Analytics", layout="wide")
load_css()
initialize_state()

st.markdown("# Analytics")
st.markdown("Track query behavior, document activity, and retrieval health.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Queries", str(len(st.session_state.get("chat_history", []))), "Total interactions")
with col2:
    render_metric_card("Documents", str(len(st.session_state.get("documents", []))), "Indexed sources")
with col3:
    render_metric_card("Chunks", str(st.session_state.get("ingestion_summary", {}).get("chunks", 0)), "Available passages")
with col4:
    render_metric_card("Backend", "Online" if st.session_state.get("backend_status", {}).get("ok") else "Offline", "Status")

fig = go.Figure(go.Bar(x=["Queries", "Documents", "Chunks"], y=[len(st.session_state.get("chat_history", [])), len(st.session_state.get("documents", [])), st.session_state.get("ingestion_summary", {}).get("chunks", 0)], marker=dict(color=["#38bdf8", "#6366f1", "#14b8a6"])))
fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
