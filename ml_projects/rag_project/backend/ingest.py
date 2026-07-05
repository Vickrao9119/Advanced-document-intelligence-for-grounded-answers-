from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Any

from chunking import Chunker
from embeddings import SimpleTfidfEmbedder
from retriever import Retriever
from vector_store import SQLiteVectorStore


class DocumentIngestor:
    def __init__(self, data_dir: str = "./data", vector_db_path: str | None = None, embedder_path: str | None = None) -> None:
        self.data_dir = data_dir
        self.vector_db_path = vector_db_path or os.path.join(data_dir, "vector_store.sqlite")
        self.embedder_path = embedder_path or os.path.join(data_dir, "embedder.pkl")
        self.chunker = Chunker()
        self.vector_store = SQLiteVectorStore(self.vector_db_path)
        self.retriever = Retriever(embedder=SimpleTfidfEmbedder(), vector_store=self.vector_store, embedder_path=self.embedder_path, store_path=self.vector_db_path)

    def ingest_directory(self, directory: str) -> Dict[str, Any]:
        documents = []
        for path in Path(directory).rglob('*'):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".pdf", ".html", ".md", ".markdown", ".txt"}:
                continue
            document_id = path.stem
            metadata = {
                "document_name": path.name,
                "file_type": path.suffix.lower(),
                "source_path": str(path),
            }
            chunks = self.chunker.ingest_file(str(path), document_id=document_id, metadata=metadata)
            documents.extend(chunks)
        self.retriever.build_index(documents)
        return {"documents_ingested": len({chunk["document_id"] for chunk in documents}), "chunks": len(documents)}

    def ingest_single_file(self, file_path: str) -> Dict[str, Any]:
        document_id = Path(file_path).stem
        metadata = {
            "document_name": Path(file_path).name,
            "file_type": Path(file_path).suffix.lower(),
            "source_path": file_path,
        }
        chunks = self.chunker.ingest_file(file_path, document_id=document_id, metadata=metadata)
        self.retriever.build_index(chunks)
        return {"documents_ingested": 1, "chunks": len(chunks)}
