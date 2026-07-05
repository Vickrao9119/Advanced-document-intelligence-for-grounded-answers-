from __future__ import annotations

import os
import sys
from pathlib import Path

from flask import Flask, jsonify, request

sys.path.append(str(Path(__file__).resolve().parent))

from generator import MockLLMGenerator
from ingest import DocumentIngestor
from retriever import Retriever

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

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
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")
    top_k = int(payload.get("top_k", 5))
    context = retriever.query(question, top_k=top_k)
    response = llm.generate(question, context)
    return jsonify({"answer": response["answer"], "citations": response["citations"], "confidence": response["confidence"], "context": context}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
