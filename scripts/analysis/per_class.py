"""Per-class test F1 at the 5% budget, mean over seeds, from one or more summary files.

    python scripts/analysis/per_class.py per_class_5seed results/v5/seeds/summary.json results/v6/ple_ensemble/summary.json
"""
import json
import sys
from collections import defaultdict

import numpy as np

from records import MODEL_NAMES, OUT, ROOT


def main(name, *summaries, tau="0.05"):
    runs = {}
    for summary in summaries:
        runs.update(json.loads((ROOT/summary).read_text())["per_seed"])
    f1 = defaultdict(dict)
    for model, seeds in runs.items():
        rows = defaultdict(list)
        for run in seeds:
            for row in run["operating_points"][tau]["test"]["per_class"]:
                rows[row["class"]].append(row["f1"])
        for cls, values in rows.items():
            f1[cls][model] = {"mean": float(np.mean(values)), "std": float(np.std(values, ddof=1)), "n": len(values)}
    models = list(runs)
    lines = [f"# Per-class test F1 ({', '.join(summaries)}; tau = {tau}, mean over seeds)", "",
             "| Class | " + " | ".join(MODEL_NAMES.get(m, m) for m in models) + " |", "|---" * (len(models)+1) + "|"]
    for cls, by_model in f1.items():
        lines.append(f"| {cls} | " + " | ".join(f"{by_model[m]['mean']:.3f}" for m in models) + " |")
    (OUT/f"{name}.json").write_text(json.dumps(f1, indent=2))
    (OUT/f"{name}_table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(*sys.argv[1:])
