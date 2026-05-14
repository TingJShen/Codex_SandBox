#!/usr/bin/env python
"""Math evaluation using HuggingFace transformers (for GPUs where vLLM custom kernels fail)."""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_dataset(dataset_name: str) -> list:
    base = "/zhdd/home/tjshen/260415_ArcherA100/eval_datasets_5090_Hao"
    paths = {
        "math500": f"{base}/math500_local/test.jsonl",
        "aime24": f"{base}/aime24_eval/train.jsonl",
        "aime25": f"{base}/aime25_local/train.jsonl",
    }
    if dataset_name == "aime24":
        jsonl_path = paths["aime24"]
        if os.path.exists(jsonl_path):
            return [json.loads(l) for l in open(jsonl_path) if l.strip()]
        arrow_path = f"{base}/aime24_eval/train/data-00000-of-00001.arrow"
        import pyarrow as pa
        table = pa.ipc.open_file(arrow_path).read_all()
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
    ans = ans.replace(",", "").replace(" ", "").lower()
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


def generate_batch(model, tokenizer, prompts, max_tokens=4096, temperature=0.0, n=1):
    """Generate responses for a batch of prompts."""
    system_msg = "You are a helpful math assistant. Solve the problem step by step and put your final answer in \\boxed{}."
    all_responses = []

    for prompt in prompts:
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096).to(model.device)

        responses = []
        for _ in range(n):
            with torch.no_grad():
                if temperature == 0.0:
                    out = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False,
                                        pad_token_id=tokenizer.eos_token_id)
                else:
                    out = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=True,
                                        temperature=temperature, top_p=0.95,
                                        pad_token_id=tokenizer.eos_token_id)
            response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            responses.append(response)
        all_responses.append(responses)

    return all_responses


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--dataset", required=True, choices=["math500", "aime24", "aime25"])
    parser.add_argument("--n-samples", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch-size", type=int, default=1)
    args = parser.parse_args()

    print(f"Loading dataset: {args.dataset}")
    dataset = load_dataset(args.dataset)
    print(f"  {len(dataset)} problems loaded")

    print(f"Loading model: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.bfloat16, device_map="cuda",
        trust_remote_code=True, attn_implementation="eager"
    )
    model.eval()
    print("Model loaded.")

    if args.n_samples == 1:
        print("Running pass@1 evaluation...")
        correct = 0
        total = len(dataset)
        results = []

        for i, item in enumerate(dataset):
            problem = item["problem"]
            gt_raw = str(item.get("answer", item.get("solution", "")))
            gt = extract_gt_answer(gt_raw)

            responses = generate_batch(model, tokenizer, [problem],
                                       max_tokens=args.max_tokens, temperature=0.0, n=1)
            resp_text = responses[0][0] if responses[0] else ""
            pred = extract_answer(resp_text) if resp_text else ""
            is_correct = check_answer(pred, gt)
            if is_correct:
                correct += 1
            results.append({"problem": problem[:80], "predicted": pred,
                           "ground_truth": gt, "correct": is_correct})

            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{total}] acc={correct/(i+1)*100:.1f}%")

        accuracy = correct / total if total > 0 else 0
        result = {"accuracy": f"{accuracy*100:.1f}%", "correct": correct,
                  "total": total, "details": results}
    else:
        print(f"Running avg@{args.n_samples} evaluation...")
        per_problem_scores = []
        results = []

        for i, item in enumerate(dataset):
            problem = item["problem"]
            gt_raw = str(item.get("answer", ""))
            gt = extract_gt_answer(gt_raw)

            responses = generate_batch(model, tokenizer, [problem],
                                       max_tokens=args.max_tokens, temperature=0.7,
                                       n=args.n_samples)
            correct_count = 0
            for resp in responses[0]:
                pred = extract_answer(resp) if resp else ""
                if check_answer(pred, gt):
                    correct_count += 1

            avg_score = correct_count / args.n_samples
            pass_score = 1.0 if correct_count > 0 else 0.0
            per_problem_scores.append(avg_score)
            results.append({"problem": problem[:80], "ground_truth": gt,
                           "avg_score": avg_score, "pass_score": pass_score,
                           "correct_count": correct_count, "n": args.n_samples})

            if (i + 1) % 5 == 0:
                avg_so_far = sum(per_problem_scores) / len(per_problem_scores)
                print(f"  [{i+1}/{len(dataset)}] avg={avg_so_far*100:.2f}%")

        avg_accuracy = sum(per_problem_scores) / len(per_problem_scores) if per_problem_scores else 0
        pass_scores = [r["pass_score"] for r in results]
        pass_accuracy = sum(pass_scores) / len(pass_scores) if pass_scores else 0
        result = {
            "avg_accuracy": f"{avg_accuracy*100:.4f}%",
            "pass_accuracy": f"{pass_accuracy*100:.4f}%",
            "num_problems": len(dataset),
            "n_samples": args.n_samples,
            "details": results,
        }

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
