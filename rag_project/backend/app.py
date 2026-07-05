from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.append(str(Path(__file__).resolve().parent))

from generator import MockLLMGenerator
from ingest import DocumentIngestor
from retriever import Retriever

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

CHAT_HISTORY_DB = os.path.join(DATA_DIR, "chat_history.sqlite")

def init_chat_history_db():
    """Initialize chat history database."""
    with sqlite3.connect(CHAT_HISTORY_DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                citations TEXT,
                confidence REAL,
                timestamp TEXT NOT NULL
            )
            """
        )
        conn.commit()
    print(f"[App] Chat history DB initialized at: {CHAT_HISTORY_DB}")

init_chat_history_db()

ingestor = DocumentIngestor(data_dir=DATA_DIR)
retriever = Retriever(embedder_path=os.path.join(DATA_DIR, "embedder.pkl"), store_path=os.path.join(DATA_DIR, "vector_store.sqlite"))
llm = MockLLMGenerator()


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@app.post("/ingest")
def ingest() -> tuple:
    directory = request.json.get("directory", os.path.join(DATA_DIR, "docs")) if request.is_json else os.path.join(DATA_DIR, "docs")
    result = ingestor.ingest_directory(directory)
    return jsonify(result), 200


@app.post("/ask")
def ask() -> tuple:
    try:
        payload = request.get_json(silent=True) or {}
        question = payload.get("question", "")
        top_k = int(payload.get("top_k", 5))
        session_id = payload.get("session_id", "default")
        context = retriever.query(question, top_k=top_k)
        response = llm.generate(question, context)
        
        # Save to chat history
        with sqlite3.connect(CHAT_HISTORY_DB) as conn:
            conn.execute(
                """
                INSERT INTO conversations (session_id, question, answer, citations, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    question,
                    response["answer"],
                    json.dumps(response["citations"]),
                    response["confidence"],
                    datetime.now().isoformat()
                )
            )
            conn.commit()
        print(f"[App] Saved conversation to history for session: {session_id}")
        
        return jsonify({"answer": response["answer"], "citations": response["citations"], "confidence": response["confidence"], "context": context}), 200
    except RuntimeError as exc:
        return jsonify({"error": str(exc), "answer": "No documents have been ingested yet. Please upload documents first.", "citations": [], "confidence": 0.0, "context": []}), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "answer": "An error occurred processing your question.", "citations": [], "confidence": 0.0, "context": []}), 200


@app.get("/history")
def get_history() -> tuple:
    """Get chat history for a session."""
    try:
        session_id = request.args.get("session_id", "default")
        with sqlite3.connect(CHAT_HISTORY_DB) as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, question, answer, citations, confidence, timestamp
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp ASC
                """,
                (session_id,)
            ).fetchall()
        
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "session_id": row[1],
                "question": row[2],
                "answer": row[3],
                "citations": json.loads(row[4]) if row[4] else [],
                "confidence": row[5],
                "timestamp": row[6]
            })
        
        print(f"[App] Retrieved {len(history)} conversations for session: {session_id}")
        return jsonify({"history": history}), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "history": []}), 200


@app.delete("/history")
def clear_history() -> tuple:
    """Clear chat history for a session."""
    try:
        session_id = request.args.get("session_id", "default")
        with sqlite3.connect(CHAT_HISTORY_DB) as conn:
            conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()
        print(f"[App] Cleared history for session: {session_id}")
        return jsonify({"message": "History cleared"}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
