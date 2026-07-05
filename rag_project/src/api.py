from __future__ import annotations

from typing import Any

import requests


class RagAPIClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/") if base_url else "http://127.0.0.1:8000"

    def health_check(self) -> dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            if response.ok:
                return {"ok": True, "status": response.json().get("status", "ok")}
            return {"ok": False, "error": response.text}
        except Exception as exc:  # pragma: no cover - network-dependent
            return {"ok": False, "error": str(exc)}

    def ingest_documents(self, directory: str) -> dict[str, Any]:
        try:
            response = requests.post(f"{self.base_url}/ingest", json={"directory": directory}, timeout=90)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover - network-dependent
            return {"error": str(exc)}

    def ask_question(self, question: str, top_k: int = 5, session_id: str = "default") -> dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                json={"question": question, "top_k": top_k, "session_id": session_id},
                timeout=90,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover - network-dependent
            return {"error": str(exc), "answer": "The backend could not answer the question right now."}

    def get_history(self, session_id: str = "default") -> dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/history", params={"session_id": session_id}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover - network-dependent
            return {"error": str(exc), "history": []}

    def clear_history(self, session_id: str = "default") -> dict[str, Any]:
        try:
            response = requests.delete(f"{self.base_url}/history", params={"session_id": session_id}, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover - network-dependent
            return {"error": str(exc)}
