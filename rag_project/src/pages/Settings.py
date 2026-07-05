from __future__ import annotations

import streamlit as st

from utils import initialize_state, load_css


st.set_page_config(page_title="Settings", layout="wide")
load_css()
initialize_state()

st.markdown("# Settings")
st.markdown("Tune retrieval behavior for the connected backend.")

settings = st.session_state.setdefault("settings", {})
settings["chunk_size"] = st.slider("Chunk size", min_value=200, max_value=1200, value=int(settings.get("chunk_size", 600)))
settings["overlap"] = st.slider("Overlap", min_value=40, max_value=300, value=int(settings.get("overlap", 120)))
settings["top_k"] = st.slider("Top-K", min_value=1, max_value=10, value=int(settings.get("top_k", 5)))
settings["temperature"] = st.slider("Temperature", min_value=0.0, max_value=1.0, value=float(settings.get("temperature", 0.2)))
settings["embedding_model"] = st.selectbox("Embedding model", ["Offline TF-IDF", "SentenceTransformers", "OpenAI text-embedding-3"], index=0)

st.success("Settings are saved in your current Streamlit session.")
