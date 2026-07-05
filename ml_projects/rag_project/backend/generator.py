from __future__ import annotations

from typing import List, Dict, Any


class MockLLMGenerator:
    """A deterministic offline generator that mimics a grounded LLM response."""

    def generate(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not context_chunks:
            return {
                "answer": "I couldn't find enough relevant information in the uploaded documents.",
                "citations": [],
                "confidence": 0.0,
            }

        joined = "\n\n".join(chunk["content"] for chunk in context_chunks[:3])
        answer = (
            f"Based on the uploaded content, here is a grounded summary.\n\n{joined[:900]}"
        )
        citations = [
            {
                "document": chunk.get("metadata", {}).get("document_name", chunk.get("source_path", "unknown")),
                "chunk_id": chunk.get("chunk_id", "n/a"),
                "source_path": chunk.get("source_path", "unknown"),
            }
            for chunk in context_chunks[:3]
        ]
        return {
            "answer": answer,
            "citations": citations,
            "confidence": round(min(0.98, 0.4 + 0.12 * len(context_chunks)), 2),
        }
