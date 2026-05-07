# Remote Paths and Resume Commands

## Shared Root

```text
/zhdd/home/tjshen/260415_ArcherA100
```

## Archived Scripts on Remote

```text
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_answers_priority_20260507.sh
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_judge_priority_20260507.sh
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_token_usage.py
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_tolerant_summary.py
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_qwen3_arena_p1_20260507.tsv
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_v11_arena_p2_20260507.tsv
```

## Work Directories

```text
/zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1
/zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507
```

## Diagnostics

```text
/zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507
```

Useful stdout logs:

```text
/zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/qwen3_p1_answers_retry1_5090hao_gpu0.out
/zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/qwen3_p1_judge_retry1_8a100_gpu4.out
/zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/v11_p2_answers_retry1_5090lian_gpu1.out
/zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/v11_p2_judge_8a100_gpu4.out
```

## Monitoring Commands

Qwen3 answer counts:

```bash
ssh 5090_Hao 'for f in /zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1/data/arena-hard-v2.0/model_answer/*.jsonl; do [ -e "$f" ] && printf "%s\t" "$(basename "$f")" && wc -l < "$f"; done | sort'
```

V11 answer counts:

```bash
ssh 5090_Lian 'for f in /zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507/data/arena-hard-v2.0/model_answer/ArcherCodeR-V11-step*-merged.jsonl; do [ -e "$f" ] && printf "%s\t" "$(basename "$f")" && wc -l < "$f"; done | sort -V'
```

Judge watcher status:

```bash
ssh 8A100 'ps -eo pid,stat,etime,cmd | grep arena_judge_priority_20260507 | grep -v grep'
```

Judge output counts:

```bash
ssh 8A100 'find /zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1/data/arena-hard-v2.0/model_judgment -type f -name "*.jsonl" 2>/dev/null | while read f; do printf "%s\t" "$(basename "$f")"; wc -l < "$f"; done | sort'
ssh 8A100 'find /zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507/data/arena-hard-v2.0/model_judgment -type f -name "*.jsonl" 2>/dev/null | while read f; do printf "%s\t" "$(basename "$f")"; wc -l < "$f"; done | sort -V'
```

A100 judge GPU memory:

```bash
ssh 8A100 'nvidia-smi --id=4 --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits'
```

## Resume Qwen3 P1 Answer Generation

Use this only if the existing Qwen3 answer process has stopped before all manifest models reached `750/750`.

```bash
ssh 5090_Hao 'mkdir -p /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507; RUN_ID=arena_priority_qwen3_p1_20260507_retry1 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_qwen3_arena_p1_20260507.tsv ANSWER_GPU=0 ANSWER_PORT=9961 ANSWER_GPU_MEMORY_UTILIZATION=0.55 USE_QWEN3_MM_FIX=1 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_answers_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/qwen3_p1_answers_retry1_5090hao_gpu0.out 2>&1 &'
```

The script skips any answer file already at `750/750`.

## Resume V11 P2 Answer Generation

Use this only if the existing V11 answer process has stopped before all manifest models reached `750/750`.

```bash
ssh 5090_Lian 'mkdir -p /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507; RUN_ID=arena_priority_v11_p2_20260507 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_v11_arena_p2_20260507.tsv ANSWER_GPU=1 ANSWER_PORT=9962 ANSWER_GPU_MEMORY_UTILIZATION=0.55 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_answers_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/v11_p2_answers_retry1_5090lian_gpu1.out 2>&1 &'
```

The script skips any answer file already at `750/750`.

## Resume Judge Watchers

Qwen3 P1 judge:

```bash
ssh 8A100 'RUN_ID=arena_priority_qwen3_p1_20260507_retry1 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_qwen3_arena_p1_20260507.tsv JUDGE_GPU=4 JUDGE_PORT=9963 JUDGE_MAX_USED_MEM_MIB=4096 GPU_POLL_INTERVAL_SEC=120 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_judge_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/qwen3_p1_judge_retry1_8a100_gpu4.out 2>&1 &'
```

V11 P2 judge:

```bash
ssh 8A100 'RUN_ID=arena_priority_v11_p2_20260507 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_v11_arena_p2_20260507.tsv JUDGE_GPU=4 JUDGE_PORT=9964 JUDGE_MAX_USED_MEM_MIB=4096 GPU_POLL_INTERVAL_SEC=120 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_judge_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/v11_p2_judge_8a100_gpu4.out 2>&1 &'
```

## Record Final Results

After judge completion, summarize and record:

```bash
python /zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1/scripts/arena_tolerant_summary.py --judgment-dir /zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1/data/arena-hard-v2.0/model_judgment/Qwen2.5-32B-Instruct --output /zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1/arena_tolerant_summary.csv --bad-label-output /zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1/arena_tolerant_bad_labels.csv
python /zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507/scripts/arena_tolerant_summary.py --judgment-dir /zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507/data/arena-hard-v2.0/model_judgment/Qwen2.5-32B-Instruct --output /zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507/arena_tolerant_summary.csv --bad-label-output /zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507/arena_tolerant_bad_labels.csv
```
