from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from judge import MockJudge


class EvaluationRunner:
    def __init__(self, data_path: str = "./data", output_path: str = "./reports/results.csv") -> None:
        self.data_path = data_path
        self.output_path = output_path
        self.judge = MockJudge()

    def load_questions(self, path: str | None = None) -> List[Dict[str, Any]]:
        file_path = path or os.path.join(self.data_path, "questions.json")
        with open(file_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def run(self, questions_path: str | None = None) -> List[Dict[str, Any]]:
        questions = self.load_questions(questions_path)
        results = []
        for item in questions:
            evaluation = self.judge.evaluate(
                question=item["question"],
                answer=item.get("answer", ""),
                context=item.get("context", ""),
                reference=item.get("reference"),
            )
            results.append({**item, **evaluation})
        self._write_csv(results)
        return results

    def _write_csv(self, results: List[Dict[str, Any]]) -> None:
        out_dir = Path(self.output_path).parent
        out_dir.mkdir(parents=True, exist_ok=True)
        fieldnames = ["question", "answer", "context", "reference", "faithfulness", "answer_relevance", "overall"]
        with open(self.output_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow({key: row.get(key, "") for key in fieldnames})
