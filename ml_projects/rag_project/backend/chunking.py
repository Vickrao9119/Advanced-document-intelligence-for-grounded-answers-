from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import List, Dict, Any


class Chunker:
    """Split documents into overlapping chunks and produce deterministic chunk IDs."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 120) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, document_id: str, source_path: str, metadata: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        metadata = metadata or {}
        cleaned = " ".join(text.split())
        if not cleaned:
            return []
        chunks: List[Dict[str, Any]] = []
        start = 0
        index = 0
        while start < len(cleaned):
            end = min(start + self.chunk_size, len(cleaned))
            segment = cleaned[start:end]
            chunk_id = self._hash_chunk(document_id, source_path, index, segment)
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "source_path": source_path,
                    "content": segment,
                    "metadata": {
                        **metadata,
                        "chunk_index": index,
                        "chunk_length": len(segment),
                    },
                }
            )
            if end >= len(cleaned):
                break
            start += self.chunk_size - self.chunk_overlap
            index += 1
        return chunks

    def read_text_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()

    def read_pdf_text(self, path: str) -> str:
        try:
            from PyPDF2 import PdfReader
        except ImportError as exc:
            raise RuntimeError("PyPDF2 is required for PDF ingestion") from exc
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def read_html_text(self, path: str) -> str:
        from bs4 import BeautifulSoup
        with open(path, "r", encoding="utf-8") as handle:
            soup = BeautifulSoup(handle.read(), "html.parser")
            return soup.get_text("\n")

    def read_markdown_text(self, path: str) -> str:
        return self.read_text_file(path)

    def ingest_file(self, path: str, document_id: str, metadata: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        suffix = Path(path).suffix.lower()
        if suffix == ".pdf":
            text = self.read_pdf_text(path)
        elif suffix == ".html":
            text = self.read_html_text(path)
        elif suffix in {".md", ".markdown", ".txt"}:
            text = self.read_markdown_text(path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        return self.chunk_text(text, document_id, path, metadata=metadata)

    @staticmethod
    def _hash_chunk(document_id: str, source_path: str, index: int, content: str) -> str:
        payload = f"{document_id}|{source_path}|{index}|{content}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:16]
