# V13 Training Archive, 2026-05-07

This folder records the V13 data-mixing training operations that were run or prepared on the shared `/zhdd` servers.

The archive is intentionally lightweight. It keeps procedures, exact parameters, failure analysis, watcher logic, and small log excerpts. It does not include model checkpoints, generated rollouts, Ray object stores, or full `train.log` files.

## Files

| File | Purpose |
| --- | --- |
| `V13_TRAINING_WORKFLOW_20260507.md` | End-to-end training workflow, environment, launch parameters, and operational rules. |
| `V13_TRAINING_RESULTS_20260507.md` | Attempt-by-attempt status table, observed results, failure causes, and current watcher state. |
| `../scripts/train_v13_8a100_gpus0_7_wait_free_bsz96.sh` | Reproducible watcher/launcher script for the current GPU0/GPU7 plan. |
| `../logs/v13_8a100_gpus0_7_bsz64_oom_excerpt.log` | Minimal excerpt of the key `bsz64` run result and OOM cause. |
| `../logs/watcher_gpus0_7_q25_bsz96_20260507_excerpt.log` | Minimal excerpt of the waiting watcher state. |

## Remote Roots

```text
/zhdd/home/tjshen/260415_ArcherA100/v13
/zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu
/home/tjshen/v13_run_q25_20260506_173125
```

The shared output root for the latest 8A100 Qwen2.5-1.5B runs is:

```text
/zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu/ArcherCodeR-V13-Qwen25-1_5B-8A100
```
