from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import numpy as np


class MockJudge:
    """A deterministic offline judge that scores answer quality heuristically."""

    def evaluate(self, question: str, answer: str, context: str, reference: str | None = None) -> Dict[str, Any]:
        context_tokens = set(context.lower().split())
        answer_tokens = set(answer.lower().split())
        overlap = len(context_tokens & answer_tokens) / max(1, len(answer_tokens))
        faithfulness = round(min(1.0, overlap + 0.1), 2)
        relevance = round(min(1.0, 0.2 + overlap), 2)
        if reference:
            ref_tokens = set(reference.lower().split())
            ref_overlap = len(ref_tokens & answer_tokens) / max(1, len(ref_tokens))
            relevance = round(min(1.0, 0.5 * relevance + 0.5 * ref_overlap), 2)
        return {
            "faithfulness": faithfulness,
            "answer_relevance": relevance,
            "overall": round((faithfulness + relevance) / 2.0, 2),
        }
