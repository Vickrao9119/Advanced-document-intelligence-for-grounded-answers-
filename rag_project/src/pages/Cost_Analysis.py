from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from components import render_metric_card
from utils import initialize_state, load_css


st.set_page_config(page_title="Cost Analysis", layout="wide")
load_css()
initialize_state()

st.markdown("# Cost Analysis")
st.markdown("Estimate operating cost for local and managed vector storage strategies.")

col1, col2, col3 = st.columns(3)
with col1:
    render_metric_card("100K Vectors", "$18/mo", "Local SQLite")
with col2:
    render_metric_card("1M Vectors", "$62/mo", "Managed DB")
with col3:
    render_metric_card("10M Vectors", "$420/mo", "Managed DB")

labels = ["100K", "1M", "10M"]
local_costs = [18, 62, 420]
managed_costs = [30, 95, 650]
fig = go.Figure()
fig.add_trace(go.Bar(name="Local", x=labels, y=local_costs, marker_color="#38bdf8"))
fig.add_trace(go.Bar(name="Managed", x=labels, y=managed_costs, marker_color="#8b5cf6"))
fig.update_layout(height=340, barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
