from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

import numpy as np

from embeddings import SimpleTfidfEmbedder
from vector_store import SQLiteVectorStore


class Retriever:
    def __init__(self, embedder: Optional[SimpleTfidfEmbedder] = None, vector_store: Optional[SQLiteVectorStore] = None, embedder_path: str | None = None, store_path: str | None = None) -> None:
        self.embedder = embedder or SimpleTfidfEmbedder()
        self.vector_store = vector_store or SQLiteVectorStore(store_path or "./data/vector_store.sqlite")
        self.embedder_path = embedder_path or "./data/embedder.pkl"
        self.store_path = store_path or "./data/vector_store.sqlite"

    def build_index(self, chunks: List[Dict[str, object]]) -> None:
        texts = [chunk["content"] for chunk in chunks]
        self.embedder.fit(texts)
        embeddings = self.embedder.embed(texts)
        for chunk, embedding in zip(chunks, embeddings):
            self.vector_store.upsert(
                chunk_id=str(chunk["chunk_id"]),
                document_id=str(chunk["document_id"]),
                source_path=str(chunk["source_path"]),
                content=str(chunk["content"]),
                metadata=dict(chunk["metadata"]),
                embedding=embedding,
            )
        self.embedder.save(self.embedder_path)

    def query(self, question: str, top_k: int = 5, filters: Optional[Dict[str, object]] = None) -> List[Dict[str, object]]:
        if not self.embedder._fitted:
            if os.path.exists(self.embedder_path):
                self.embedder = SimpleTfidfEmbedder.load(self.embedder_path)
            else:
                raise RuntimeError("Index has not been built yet.")
        query_embedding = self.embedder.embed([question])[0]
        return self.vector_store.search(query_embedding=query_embedding, top_k=top_k, filters=filters)
