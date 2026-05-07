#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

import tiktoken


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "answer" in value:
            return as_text(value["answer"])
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "\n".join(as_text(v) for v in value)
    return str(value)


def count_tokens(encoding, value):
    return len(encoding.encode(as_text(value), disallowed_special=()))


def iter_jsonl(path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def answer_usage(work_dir, model, encoding):
    path = work_dir / "data" / "arena-hard-v2.0" / "model_answer" / f"{model}.jsonl"
    requests = 0
    input_tokens = 0
    output_tokens = 0
    for row in iter_jsonl(path) or []:
        requests += 1
        messages = row.get("messages", [])
        if messages:
            input_tokens += sum(count_tokens(encoding, m.get("content", "")) for m in messages[:-1])
            output_tokens += count_tokens(encoding, messages[-1].get("content", ""))
    return requests, input_tokens, output_tokens


def judgment_usage(work_dir, judge, model, encoding):
    path = work_dir / "data" / "arena-hard-v2.0" / "model_judgment" / judge / f"{model}.jsonl"
    requests = 0
    input_tokens = 0
    output_tokens = 0
    scored_questions = 0
    null_games = 0
    for row in iter_jsonl(path) or []:
        scored_questions += 1
        for game in row.get("games", []):
            requests += 1
            if not game:
                null_games += 1
                continue
            input_tokens += sum(count_tokens(encoding, m.get("content", "")) for m in game.get("prompt", []))
            output_tokens += count_tokens(encoding, game.get("judgment", ""))
    return requests, input_tokens, output_tokens, scored_questions, null_games


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--judge", default="gpt-4o-mini")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    work_dir = Path(args.work_dir)
    encoding = tiktoken.encoding_for_model("gpt-4o")
    rows = []

    totals = {
        "answer_requests": 0,
        "answer_input_tokens": 0,
        "answer_output_tokens": 0,
        "judge_requests": 0,
        "judge_input_tokens": 0,
        "judge_output_tokens": 0,
        "scored_questions": 0,
        "null_judge_games": 0,
    }

    for model in args.models:
        ar, ai, ao = answer_usage(work_dir, model, encoding)
        jr, ji, jo, sq, ng = judgment_usage(work_dir, args.judge, model, encoding)
        row = {
            "model": model,
            "answer_requests": ar,
            "answer_input_tokens": ai,
            "answer_output_tokens": ao,
            "judge_requests": jr,
            "judge_input_tokens": ji,
            "judge_output_tokens": jo,
            "scored_questions": sq,
            "null_judge_games": ng,
            "total_requests": ar + jr,
            "total_input_tokens": ai + ji,
            "total_output_tokens": ao + jo,
            "total_tokens": ai + ao + ji + jo,
        }
        rows.append(row)
        for key in totals:
            totals[key] += row[key]

    total_row = {
        "model": "__TOTAL__",
        **totals,
        "total_requests": totals["answer_requests"] + totals["judge_requests"],
        "total_input_tokens": totals["answer_input_tokens"] + totals["judge_input_tokens"],
        "total_output_tokens": totals["answer_output_tokens"] + totals["judge_output_tokens"],
        "total_tokens": (
            totals["answer_input_tokens"]
            + totals["answer_output_tokens"]
            + totals["judge_input_tokens"]
            + totals["judge_output_tokens"]
        ),
    }
    rows.append(total_row)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(output)


if __name__ == "__main__":
    main()
