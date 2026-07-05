from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from api import RagAPIClient
from components import render_citation_cards, render_metric_card
from utils import initialize_state, load_css, resolve_backend_url


st.set_page_config(page_title="Chat", layout="wide")
load_css()
initialize_state()

client = RagAPIClient(resolve_backend_url())

st.markdown("# Ask AI")
st.markdown("Ask a question and receive a grounded answer backed by document evidence.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_container = st.container()
with chat_container:
    for entry in st.session_state.chat_history:
        if entry["role"] == "user":
            st.markdown(f"**You:** {entry['content']}")
        else:
            st.markdown(f"**Assistant:** {entry['content']}")
            if entry.get("citations"):
                render_citation_cards(entry["citations"])
            if entry.get("confidence") is not None:
                st.caption(f"Confidence: {entry['confidence']}")

question = st.text_input("Ask about your documents", placeholder="What is mentioned about the project scope?")
if st.button("Send") and question.strip():
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.spinner("Retrieving relevant context..."):
        result = client.ask_question(question, top_k=st.session_state.get("settings", {}).get("top_k", 5))
    if result.get("error"):
        st.error(result["error"])
        st.session_state.chat_history.append({"role": "assistant", "content": "The backend could not answer the question right now."})
    else:
        assistant_message = {
            "role": "assistant",
            "content": result.get("answer", ""),
            "citations": result.get("citations", []),
            "confidence": result.get("confidence"),
        }
        st.session_state.chat_history.append(assistant_message)
        st.rerun()

col1, col2 = st.columns(2)
with col1:
    render_metric_card("Total Exchange", str(len(st.session_state.chat_history)), "Conversation turns")
with col2:
    render_metric_card("Latest Confidence", str(st.session_state.chat_history[-1].get("confidence", "n/a")) if st.session_state.chat_history else "n/a", "Most recent answer")
