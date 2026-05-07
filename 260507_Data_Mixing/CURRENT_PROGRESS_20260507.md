# Current Progress Snapshot

Last successful live check:

```text
2026-05-07 06:54 UTC
2026-05-07 14:54 Asia/Shanghai
```

After this point, several SSH attempts were reset by the gateway, so this file records the most recent verified state rather than an unverified later estimate.

## Arena Answer Generation

| Queue | Server/GPU | Current/Completed Model | Answer Rows |
| --- | --- | --- | ---: |
| Qwen3 P1 | `5090_Hao GPU0` | `Qwen3-2B-base` | `750/750` |
| Qwen3 P1 | `5090_Hao GPU0` | `ArcherCodeR-V12-Qwen3-2B-8A100-step100` | `190/750` |
| V11 P2 | `5090_Lian GPU1` | `ArcherCodeR-V11-step80-merged` | `750/750` |
| V11 P2 | `5090_Lian GPU1` | `ArcherCodeR-V11-step160-merged` | `750/750` |
| V11 P2 | `5090_Lian GPU1` | `ArcherCodeR-V11-step320-merged` | `750/750` |
| V11 P2 | `5090_Lian GPU1` | `ArcherCodeR-V11-step400-merged` | `750/750` |
| V11 P2 | `5090_Lian GPU1` | `ArcherCodeR-V11-step480-merged` | `750/750` |
| V11 P2 | `5090_Lian GPU1` | `ArcherCodeR-V11-step560-merged` | `637/750` |

## Judge Watchers

| Queue | PID | Server/GPU | State |
| --- | ---: | --- | --- |
| Qwen3 P1 judge | `110531` | `8A100 GPU4` | Waiting for all Qwen3 P1 answer files to reach `750/750`. |
| V11 P2 judge | `92541` | `8A100 GPU4` | Waiting for all V11 P2 answer files to reach `750/750`. |

No new judgment files had been produced at the last successful live check because the manifests were not fully answered yet.

## A100 Judge GPU Memory

Last observed:

```text
8A100 GPU4 memory.used = 68902 MiB / 81920 MiB
```

The watcher threshold is:

```text
JUDGE_MAX_USED_MEM_MIB=4096
```

So even after answer generation finishes, judge startup will wait until GPU4 memory is mostly free.

## Pending Work

| Priority | Work |
| --- | --- |
| P1 | Finish all Qwen3 P1 answer files, then run local 32B judge. |
| P2 | Finish all V11 P2 answer files, then run local 32B judge. |
| P3 | Record `arena_tolerant_summary.csv` and `arena_token_usage.csv` into `eval_result_log_1_5B.md` after judgment completes. |
| P4 | Decide whether to merge/evaluate the many later raw Qwen3-2B 5090_Lian step100 checkpoints from 2026-04-30 to 2026-05-06. |
