from __future__ import annotations

import math
import pickle
from collections import Counter
from typing import List

import numpy as np


class SimpleTfidfEmbedder:
    """A lightweight, offline-friendly TF-IDF embedder implemented with NumPy."""

    def __init__(self, max_features: int = 4096) -> None:
        self.model_name = "tfidf-offline-v1"
        self.max_features = max_features
        self.vocabulary: dict[str, int] = {}
        self.idf: np.ndarray | None = None
        self._fitted = False

    @property
    def dim(self) -> int:
        return len(self.vocabulary) if self._fitted else 0

    def fit(self, texts: List[str]) -> None:
        tokenized = [self._tokenize(text) for text in texts]
        vocab = {}
        for tokens in tokenized:
            for token in set(tokens):
                vocab.setdefault(token, len(vocab))
        if self.max_features and len(vocab) > self.max_features:
            vocab = {token: idx for idx, token in enumerate(sorted(vocab)[: self.max_features])}

        self.vocabulary = vocab
        doc_count = len(tokenized)
        df = np.zeros(len(vocab), dtype=np.float32)
        for tokens in tokenized:
            seen = set(tokens)
            for token in seen:
                if token in vocab:
                    df[vocab[token]] += 1.0
        idf = np.log((1 + doc_count) / (1 + df)) + 1.0
        self.idf = idf.astype(np.float32)
        self._fitted = True

    def transform(self, texts: List[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Embedder must be fit() before embedding text.")
        rows = []
        for text in texts:
            tokens = self._tokenize(text)
            counts = Counter(token for token in tokens if token in self.vocabulary)
            row = np.zeros(len(self.vocabulary), dtype=np.float32)
            for token, count in counts.items():
                idx = self.vocabulary[token]
                row[idx] = count
            rows.append(row)
        matrix = np.vstack(rows).astype(np.float32)
        if self.idf is None:
            raise RuntimeError("IDF weights were not initialized.")
        weighted = matrix * self.idf
        norms = np.linalg.norm(weighted, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return weighted / norms

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.transform(texts)

    def save(self, path: str) -> None:
        with open(path, "wb") as handle:
            pickle.dump(
                {
                    "model_name": self.model_name,
                    "max_features": self.max_features,
                    "vocabulary": self.vocabulary,
                    "idf": self.idf,
                    "fitted": self._fitted,
                },
                handle,
            )

    @classmethod
    def load(cls, path: str) -> "SimpleTfidfEmbedder":
        with open(path, "rb") as handle:
            payload = pickle.load(handle)
        obj = cls(max_features=payload.get("max_features", 4096))
        obj.model_name = payload.get("model_name", "tfidf-offline-v1")
        obj.vocabulary = payload.get("vocabulary", {})
        obj.idf = payload.get("idf")
        obj._fitted = payload.get("fitted", False)
        return obj

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        cleaned = " ".join(text.lower().replace("\n", " ").split())
        return [token for token in cleaned.replace("/", " ").replace("-", " ").split() if token]
