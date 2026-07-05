from __future__ import annotations

import os
import sys

from evaluation import EvaluationRunner


if __name__ == "__main__":
    runner = EvaluationRunner(data_path=os.path.join(os.path.dirname(__file__), "..", "data"), output_path=os.path.join(os.path.dirname(__file__), "..", "reports", "results.csv"))
    results = runner.run()
    print(f"Evaluated {len(results)} items")
    print("Results written to", runner.output_path)
