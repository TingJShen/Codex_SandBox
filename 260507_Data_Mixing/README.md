# 260507 Data Mixing Evaluation Archive

This directory archives the 2026-05-07 Data Mixing / ArcherCodeR evaluation work.

It is intentionally lightweight: it keeps procedures, manifests, scripts, result tables, and small cache files needed to reproduce the evaluation workflow. It does not include model checkpoints, generated answer JSONL files, judgment JSONL files, or other large outputs.

## Contents

| Path | Purpose |
| --- | --- |
| `TESTING_WORKFLOW.md` | Full evaluation workflow, launch commands, failure analysis, fixes, and monitoring logic. |
| `RESULTS_SUMMARY.md` | Compact result summary for math, code, and Arena-Hard. |
| `BATCH_AWARE_DATA_SHAPLEY_GRPO_V13_20260515.md` | Batch-aware Taylor / Data Shapley formulation for the planned V13 GRPO sampler. |
| `CURRENT_PROGRESS_20260507.md` | Last successful live progress snapshot and pending work. |
| `REMOTE_PATHS_AND_RESUME.md` | Remote paths, resume commands, and monitoring commands. |
| `results/latest_20260519/` | Small CSV backups from the 2026-05-19 server result backfill. |
| `code/` | Lightweight V13 source-code snapshot with large/generated files excluded. |
| `training/` | V13 training workflow, attempt table, live GPU0/GPU7 watcher state, and OOM analysis. |
| `results/eval_result_log_1_5B.md` | Full local result log copied from `D:\Codex_Sandbox\Huawei_Hard\eval_result_log_1_5B.md`. |
| `scripts/` | Arena-Hard answer/judge drivers and summary utilities used for the 2026-05-07 priority sweep. |
| `logs/` | Small V13 training and watcher log excerpts; full logs remain on `/zhdd`. |
| `manifests/` | Model manifests for Qwen3 P1 and V11 P2 Arena sweeps. |
| `support_cache/o200k_base.tiktoken` | Small `tiktoken` BPE cache file used to avoid remote download failure. |

## Main Evaluation Roots

Remote shared root:

```text
/zhdd/home/tjshen/260415_ArcherA100
```

Important result/log roots:

```text
/zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1
/zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507
/zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507
/zhdd/home/tjshen/260415_ArcherA100/eval_results_qwen3_2b_20260424_mmfix
/zhdd/home/tjshen/260415_ArcherA100/eval_results_qwen3_2b_new_ckpt_20260427_mmfix
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_temp06_all_20260422_171825
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_temp06_v12_600_800_20260424_1220
```

## High-Level Status

As of the last successful live check on 2026-05-07 06:54 UTC:

| Queue | Status |
| --- | --- |
| Qwen3 Arena P1 | Base answer finished `750/750`; `ArcherCodeR-V12-Qwen3-2B-8A100-step100` answer running, last observed `190/750`. |
| V11 Arena P2 | step80/160/320/400/480 answer finished `750/750`; step560 running, last observed `637/750`. |
| Arena judge | Watchers are alive but waiting for all answers in each manifest plus enough A100 GPU memory. |
| Existing math/code | Recorded in `results/eval_result_log_1_5B.md`; 1.5B V11/V12 and selected Qwen3-2B models have math/code coverage. |
| Existing Arena temp=0.6 | 1.5B base, V11 step240, and V12 step100-800 are complete in the local log. |
| V13 training | `sample_taylor_v13` route verified to enter step 1 on 8A100 GPU0/GPU7; `bsz64` failed at actor optimizer because other users occupied most of GPU0/GPU7. A watcher is waiting to relaunch `bsz96/mini48/util0.70` when both cards have at least 70000 MiB free. |

## Important Operational Rules

The remote runs were operated under these constraints:

```text
Do not use rm.
Do not use /tmp.
Put logs/scripts/temp/cache under /zhdd/home/tjshen/260415_ArcherA100.
Check GPU memory capacity, not utilization, when deciding whether a GPU can accept a job.
Prefer environment/cache fixes over changing model/evaluation logic.
```

## Latest V13 Training Notes

The current V13 training archive is under:

```text
training/
```

Start with:

```text
training/V13_TRAINING_WORKFLOW_20260507.md
training/V13_TRAINING_RESULTS_20260507.md
```
