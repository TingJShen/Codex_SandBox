#!/usr/bin/env python
"""Lightweight math evaluation via vLLM OpenAI-compatible API."""

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


def load_dataset(dataset_name: str) -> list:
    base = "/zhdd/home/tjshen/260415_ArcherA100/eval_datasets_5090_Hao"
    paths = {
        "math500": f"{base}/math500_local/test.jsonl",
        "aime24": f"{base}/aime24_eval/train/data-00000-of-00001.arrow",
        "aime25": f"{base}/aime25_local/train.jsonl",
    }
    if dataset_name == "aime24":
        jsonl_path = f"{base}/aime24_eval/train.jsonl"
        if os.path.exists(jsonl_path):
            return [json.loads(l) for l in open(jsonl_path) if l.strip()]
        import pyarrow as pa
        table = pa.ipc.open_file(paths["aime24"]).read_all()
        return [{"problem": str(table.column("problem")[i].as_py()),
                 "answer": str(table.column("answer")[i].as_py()),
                 "id": str(i)} for i in range(len(table))]
    path = paths[dataset_name]
    return [json.loads(l) for l in open(path) if l.strip()]


def extract_boxed_nested(text: str) -> str:
    idx = text.rfind("\\boxed{")
    if idx < 0:
        return None
    i = idx + len("\\boxed{")
    depth = 1
    start = i
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i].strip()
        i += 1
    return None


def extract_answer(text: str) -> str:
    boxed = extract_boxed_nested(text)
    if boxed is not None:
        return boxed
    patterns = [
        r"[Tt]he\s+(?:final\s+)?answer\s+is[:\s]*\$?([^$\n.]+)",
        r"[Aa]nswer[:\s]*\$?([^$\n.]+)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(1).strip()
    lines = text.strip().split("\n")
    for line in reversed(lines):
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return text.strip()


def extract_gt_answer(gt_raw: str) -> str:
    boxed = extract_boxed_nested(gt_raw)
    if boxed is not None:
        return boxed
    return gt_raw


def normalize_answer(ans: str) -> str:
    ans = str(ans).strip()
    ans = ans.replace("\\$", "").replace("$", "")
    ans = ans.replace("\\%", "").replace("%", "")
    ans = ans.replace("\\!", "")
    ans = ans.replace("\\,", "").replace("\\:", "").replace("\\;", "")
    ans = ans.replace("\\left", "").replace("\\right", "")
    ans = ans.replace(",", "")
    ans = ans.replace(" ", "")
    ans = ans.lower()
    frac_pat = re.compile(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}")
    while True:
        m = frac_pat.search(ans)
        if not m:
            break
        try:
            num = float(m.group(1))
            den = float(m.group(2))
            if den != 0:
                ans = ans[:m.start()] + str(num / den) + ans[m.end():]
                continue
        except (ValueError, ZeroDivisionError):
            pass
        break
    return ans


def check_answer(predicted: str, ground_truth: str) -> bool:
    pred_norm = normalize_answer(predicted)
    gt_norm = normalize_answer(ground_truth)
    if pred_norm == gt_norm:
        return True
    try:
        pf = float(pred_norm)
        gf = float(gt_norm)
        if abs(pf - gf) < 1e-6:
            return True
        if gf != 0 and abs(pf - gf) / abs(gf) < 1e-4:
            return True
    except (ValueError, TypeError):
        pass
    return False


def query_model(api_base: str, model: str, prompt: str, temperature: float = 0.0,
                max_tokens: int = 32768, n: int = 1) -> list:
    url = f"{api_base}/chat/completions"
    messages = [
        {"role": "system", "content": "You are a helpful math assistant. Solve the problem step by step and put your final answer in \\boxed{}."},
        {"role": "user", "content": prompt},
    ]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "n": n,
    }
    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, timeout=600)
            resp.raise_for_status()
            data = resp.json()
            return [c["message"]["content"] for c in data["choices"]]
        except Exception as e:
            if attempt == 2:
                print(f"  ERROR after 3 attempts: {e}", file=sys.stderr)
                return [""] * n
            time.sleep(2 ** attempt)
    return [""] * n


def eval_pass_at_1(api_base: str, model: str, dataset: list, max_tokens: int = 32768, parallel: int = 8) -> dict:
    correct = 0
    total = len(dataset)
    results = []

    def process(item):
        problem = item["problem"]
        gt_raw = str(item.get("answer", item.get("solution", "")))
        gt = extract_gt_answer(gt_raw)
        responses = query_model(api_base, model, problem, temperature=0.0, max_tokens=max_tokens, n=1)
        pred = extract_answer(responses[0]) if responses[0] else ""
        is_correct = check_answer(pred, gt)
        return {"problem": problem[:80], "predicted": pred, "ground_truth": gt, "correct": is_correct}

    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = {executor.submit(process, item): i for i, item in enumerate(dataset)}
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            if r["correct"]:
                correct += 1

    accuracy = correct / total if total > 0 else 0
    return {"accuracy": f"{accuracy*100:.1f}%", "correct": correct, "total": total, "details": results}


def eval_avg_at_n(api_base: str, model: str, dataset: list, n_samples: int = 64, max_tokens: int = 32768,
                  parallel: int = 4) -> dict:
    per_problem_scores = []
    results = []

    def process(item):
        problem = item["problem"]
        gt_raw = str(item.get("answer", ""))
        gt = extract_gt_answer(gt_raw)
        responses = query_model(api_base, model, problem, temperature=0.7, max_tokens=max_tokens, n=n_samples)
        correct_count = 0
        for resp in responses:
            pred = extract_answer(resp) if resp else ""
            if check_answer(pred, gt):
                correct_count += 1
        avg_score = correct_count / len(responses) if responses else 0
        pass_score = 1.0 if correct_count > 0 else 0.0
        return {"problem": problem[:80], "ground_truth": gt, "avg_score": avg_score,
                "pass_score": pass_score, "correct_count": correct_count, "n": len(responses)}

    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = {executor.submit(process, item): i for i, item in enumerate(dataset)}
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            per_problem_scores.append(r["avg_score"])

    avg_accuracy = sum(per_problem_scores) / len(per_problem_scores) if per_problem_scores else 0
    pass_scores = [r["pass_score"] for r in results]
    pass_accuracy = sum(pass_scores) / len(pass_scores) if pass_scores else 0
    return {
        "avg_accuracy": f"{avg_accuracy*100:.4f}%",
        "pass_accuracy": f"{pass_accuracy*100:.4f}%",
        "num_problems": len(dataset),
        "n_samples": n_samples,
        "details": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-base", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--dataset", required=True, choices=["math500", "aime24", "aime25"])
    parser.add_argument("--n-samples", type=int, default=1)
    parser.add_argument("--output", required=True)
    parser.add_argument("--parallel", type=int, default=8)
    parser.add_argument("--max-tokens", type=int, default=32768)
    args = parser.parse_args()

    print(f"Loading dataset: {args.dataset}")
    dataset = load_dataset(args.dataset)
    print(f"  {len(dataset)} problems loaded")

    if args.n_samples > 1:
        print(f"Running avg@{args.n_samples} evaluation...")
        result = eval_avg_at_n(args.api_base, args.model, dataset,
                               n_samples=args.n_samples, max_tokens=args.max_tokens, parallel=args.parallel)
    else:
        print("Running pass@1 evaluation...")
        result = eval_pass_at_1(args.api_base, args.model, dataset, max_tokens=args.max_tokens, parallel=args.parallel)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {args.output}")
    if "accuracy" in result:
        print(f"  pass@1: {result['accuracy']}")
    if "avg_accuracy" in result:
        print(f"  avg@{args.n_samples}: {result['avg_accuracy']}")
        print(f"  pass@{args.n_samples}: {result['pass_accuracy']}")


if __name__ == "__main__":
    main()
