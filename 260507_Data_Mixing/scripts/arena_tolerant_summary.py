#!/usr/bin/env python3
"""Summarize Arena-Hard judgments while dropping malformed judge labels.

This does not modify raw judgments. It mirrors show_result.py's score mapping
and skips rows where either side is null or outside the supported labels.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


LABEL_TO_SCORE = {
    "A>B": [1.0],
    "A>>B": [1.0, 1.0, 1.0],
    "A=B": [0.5],
    "A<<B": [0.0, 0.0, 0.0],
    "A<B": [0.0],
    "B>A": [0.0],
    "B>>A": [0.0, 0.0, 0.0],
    "B=A": [0.5],
    "B<<A": [1.0, 1.0, 1.0],
    "B<A": [1.0],
}


def summarize_model(path: Path) -> tuple[list[dict[str, object]], Counter[str]]:
    by_category: dict[str, list[float]] = defaultdict(list)
    used_rows: Counter[str] = Counter()
    dropped_rows: Counter[str] = Counter()
    bad_labels: Counter[str] = Counter()

    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            category = str(record.get("category", "unknown"))
            games = record.get("games") or []
            if len(games) < 2 or games[0] is None or games[1] is None:
                dropped_rows[category] += 1
                bad_labels["<null>"] += 1
                continue

            score_0 = games[0].get("score")
            score_1 = games[1].get("score")
            if score_0 not in LABEL_TO_SCORE or score_1 not in LABEL_TO_SCORE:
                dropped_rows[category] += 1
                if score_0 not in LABEL_TO_SCORE:
                    bad_labels[str(score_0)] += 1
                if score_1 not in LABEL_TO_SCORE:
                    bad_labels[str(score_1)] += 1
                continue

            scores = LABEL_TO_SCORE[score_1] + [1.0 - s for s in LABEL_TO_SCORE[score_0]]
            by_category[category].extend(scores)
            used_rows[category] += 1

    rows: list[dict[str, object]] = []
    all_scores: list[float] = []
    total_used = 0
    total_dropped = 0

    for category in sorted(set(by_category) | set(used_rows) | set(dropped_rows)):
        scores = by_category.get(category, [])
        all_scores.extend(scores)
        used = used_rows[category]
        dropped = dropped_rows[category]
        total_used += used
        total_dropped += dropped
        rows.append(
            {
                "model": path.stem,
                "category": category,
                "score_percent": f"{(sum(scores) / len(scores) * 100.0):.3f}" if scores else "",
                "score_count": len(scores),
                "used_rows": used,
                "dropped_rows": dropped,
            }
        )

    rows.append(
        {
            "model": path.stem,
            "category": "__overall__",
            "score_percent": f"{(sum(all_scores) / len(all_scores) * 100.0):.3f}" if all_scores else "",
            "score_count": len(all_scores),
            "used_rows": total_used,
            "dropped_rows": total_dropped,
        }
    )
    return rows, bad_labels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judgment-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bad-label-output", type=Path)
    args = parser.parse_args()

    all_rows: list[dict[str, object]] = []
    bad_rows: list[dict[str, object]] = []
    for path in sorted(args.judgment_dir.glob("*.jsonl")):
        rows, bad_labels = summarize_model(path)
        all_rows.extend(rows)
        for label, count in sorted(bad_labels.items()):
            bad_rows.append({"model": path.stem, "bad_label": label, "count": count})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["model", "category", "score_percent", "score_count", "used_rows", "dropped_rows"],
        )
        writer.writeheader()
        writer.writerows(all_rows)

    if args.bad_label_output:
        args.bad_label_output.parent.mkdir(parents=True, exist_ok=True)
        with args.bad_label_output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["model", "bad_label", "count"])
            writer.writeheader()
            writer.writerows(bad_rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
