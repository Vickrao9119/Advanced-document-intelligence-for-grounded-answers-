from __future__ import annotations

import json
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class SQLiteVectorStore:
    """A lightweight offline vector store backed by SQLite with blob embeddings."""

    def __init__(self, db_path: str) -> None:
        self.db_path = os.path.abspath(db_path)
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        print(f"[VectorStore] Initializing database at: {self.db_path}")
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()
        print(f"[VectorStore] Database initialized successfully")

    def upsert(self, chunk_id: str, document_id: str, source_path: str, content: str, metadata: Dict[str, Any], embedding: np.ndarray) -> None:
        payload = embedding.astype(np.float32).tobytes()
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO chunks (chunk_id, document_id, source_path, content, metadata, embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (chunk_id, document_id, source_path, content, json.dumps(metadata), payload, ),
            )
            connection.commit()
        print(f"[VectorStore] Upserted chunk: {chunk_id}")

    def list_chunks(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT chunk_id, document_id, source_path, content, metadata, embedding FROM chunks"
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def search(self, query_embedding: np.ndarray, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as connection:
            sql = "SELECT chunk_id, document_id, source_path, content, metadata, embedding FROM chunks"
            clauses: List[str] = []
            params: List[Any] = []
            if filters:
                for key, value in filters.items():
                    clauses.append(f"json_extract(metadata, '$.{key}') = ?")
                    params.append(value)
            if clauses:
                sql += " WHERE " + " AND ".join(clauses)
            rows = connection.execute(sql, params).fetchall()

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for row in rows:
            embedding = np.frombuffer(row[5], dtype=np.float32)
            similarity = float(np.dot(query_embedding, embedding))
            if np.isnan(similarity):
                similarity = -1.0
            scored.append((similarity, self._row_to_dict(row)))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def delete_document(self, document_id: str) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            connection.commit()

    @staticmethod
    def _row_to_dict(row: Tuple[Any, ...]) -> Dict[str, Any]:
        chunk_id, document_id, source_path, content, metadata, embedding = row
        parsed_metadata = json.loads(metadata) if metadata else {}
        return {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "source_path": source_path,
            "content": content,
            "metadata": parsed_metadata,
        }
