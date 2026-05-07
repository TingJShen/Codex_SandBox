# Results Summary

The full detailed table is archived at:

```text
results/eval_result_log_1_5B.md
```

This file summarizes the key results known before the 2026-05-07 priority Arena sweep completes.

## Math and Code Coverage

The local result log records math and code evaluations for:

| Family | Coverage |
| --- | --- |
| `Qwen2.5-1.5B-Instruct` base | AIME24 avg@64/pass@64, AIME25 avg@64/pass@64, math500 pass@1, LCB code_generation/code_execution/test_output. |
| V11 1.5B | steps 80, 160, 240, 320, 400, 480, 560, 640, 720, 800, 880, 960, 1040. |
| V12 1.5B | steps 100, 200, 300, 400, 500, 600, 700, 800. |
| Qwen3-2B base | AIME24, AIME25, math500, LCB. |
| Qwen3-2B V12 selected checkpoints | 8A100 step100/200/300/400 and selected 5090_Lian step100 variants. |

## Qwen3-2B Math/Code Highlights

| Family | Model | Step | AIME24 avg@64 | AIME24 pass@64 | AIME25 avg@64 | AIME25 pass@64 | math500 pass@1 | LCB total | LCB mean |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3-2B Base | `Qwen3-2B-base` | base | `21.1979%` | `73.3333%` | `18.8021%` | `53.3333%` | `76.4%` | `43.70%` | `14.57%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step100` | 100 | `22.2396%` | `73.3333%` | `20.6250%` | `63.3333%` | `80.4%` | `47.49%` | `15.83%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step200` | 200 | `20.2083%` | `66.6667%` | `18.2813%` | `66.6667%` | `81.2%` | `45.21%` | `15.07%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step300` | 300 | `18.7500%` | `76.6667%` | `16.4583%` | `63.3333%` | `76.6%` | `52.98%` | `17.66%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step400` | 400 | `15.8854%` | `60.0000%` | `15.4687%` | `60.0000%` | `74.8%` | `55.84%` | `18.61%` |

## Arena-Hard temp=0.6 Completed Before This Sweep

Judge:

```text
/zhdd/models/Qwen2.5-32B-Instruct
```

The following rows were complete in `eval_result_log_1_5B.md` before the 2026-05-07 priority sweep:

| Family | Model | Step | hard_prompt | creative_writing | overall | Used rows | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Base | `Qwen2.5-1.5B-Instruct` | base | `1.284%` | `2.550%` | `1.733%` | `748/750` | complete |
| V11 | `ArcherCodeR-V11-step240-merged` | 240 | `2.298%` | `2.612%` | `2.408%` | `747/750` | complete |
| V12 | `ArcherCodeR-V12-step100-merged` | 100 | `1.718%` | `1.801%` | `1.747%` | `743/750` | complete |
| V12 | `ArcherCodeR-V12-step200-merged` | 200 | `1.374%` | `2.967%` | `1.929%` | `742/750` | complete |
| V12 | `ArcherCodeR-V12-step300-merged` | 300 | `2.417%` | `2.457%` | `2.431%` | `748/750` | complete |
| V12 | `ArcherCodeR-V12-step400-merged` | 400 | `1.944%` | `2.416%` | `2.110%` | `749/750` | complete |
| V12 | `ArcherCodeR-V12-step500-merged` | 500 | `1.780%` | `2.450%` | `2.017%` | `744/750` | complete |
| V12 | `ArcherCodeR-V12-step600-merged` | 600 | `2.338%` | `2.475%` | `2.386%` | `747/750` | complete |
| V12 | `ArcherCodeR-V12-step700-merged` | 700 | `3.091%` | `2.263%` | `2.802%` | `746/750` | complete |
| V12 | `ArcherCodeR-V12-step800-merged` | 800 | `2.916%` | `1.868%` | `2.545%` | `743/750` | complete |

## Arena-Hard GPT-4o Reference

The local log includes the official leaderboard row as a directional AB reference:

| Source | Model | Score | CI | Avg tokens |
| --- | --- | ---: | --- | ---: |
| Arena-Hard leaderboard 2024-07-31 | `gpt-4o-2024-05-13` | `79.21%` | `(-1.79, +1.50)` | `696.0` |

This is not a same-judge local 32B score. It is only an external reference anchor.

## New 2026-05-07 Arena Sweep Result Status

| Queue | Result status |
| --- | --- |
| Qwen3 P1 | Answers in progress. No local 32B judgment result yet at last successful snapshot. |
| V11 P2 | Answers in progress. No local 32B judgment result yet at last successful snapshot. |

When the two judge watchers finish, append their `arena_tolerant_summary.csv` and `arena_token_usage.csv` values to `results/eval_result_log_1_5B.md`.

## V13 Training Status Added on 2026-05-07

Detailed training notes are archived in `training/`.

| Host | GPUs | Model | Config | Status |
| --- | --- | --- | --- | --- |
| 8A100 | 0,4 | Qwen2.5-1.5B-Instruct | `bsz32`, `mini16`, `util0.40`, save100 | Smoke reached step 4, then stopped because target GPUs changed. |
| 8A100 | 0,7 | Qwen2.5-1.5B-Instruct | `bsz64`, `mini32`, `util0.60`, save100, no expandable segments | Entered `sample_taylor_v13`, fixed shadow anchors, reached V13 step 1, then failed during actor optimizer due external GPU0 memory occupation. |
| 8A100 | 0,7 | Qwen2.5-1.5B-Instruct | watcher for `bsz96`, `mini48`, `util0.70`, save100 | Waiting until GPU0 and GPU7 both have at least 70000 MiB free; not launched at the last recorded snapshot. |

No new checkpoint from the failed GPU0/GPU7 `bsz64` run. The failure was an external GPU contention issue, not a V13 method-dispatch failure.
