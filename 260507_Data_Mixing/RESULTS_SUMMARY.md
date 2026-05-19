# Results Summary

The full detailed table is archived at:

```text
results/eval_result_log_1_5B.md
```

This file summarizes the key results known through the 2026-05-19 backfill from the shared evaluation servers.

## Math and Code Coverage

The local result log records math and code evaluations for:

| Family | Coverage |
| --- | --- |
| `Qwen2.5-1.5B-Instruct` base | AIME24 avg@64/pass@64, AIME25 avg@64/pass@64, math500 pass@1, LCB code_generation/code_execution/test_output. |
| V11 1.5B | steps 80, 160, 240, 320, 400, 480, 560, 640, 720, 800, 880, 960, 1040. |
| V12 1.5B | steps 100, 200, 300, 400, 500, 600, 700, 800. |
| Qwen3-2B base | AIME24, AIME25, math500, LCB. |
| Qwen3-2B V12 selected checkpoints | 8A100 step100/200/300/400 and selected 5090_Lian step100 variants. |
| Qwen3-2B V13 / V13 GradSketch | Original V13 step200, GradSketch step200/300, plus quick V13grad step10/step100 backfill. |
| V14 round6 Qwen2.5-1.5B | steps 50, 100, 150, 200 for Math500, AIME24/AIME25 avg@64/pass@64, and LCB. |

## Qwen3-2B Math/Code Highlights

| Family | Model | Step | AIME24 avg@64 | AIME24 pass@64 | AIME25 avg@64 | AIME25 pass@64 | math500 pass@1 | LCB total | LCB mean |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3-2B Base | `Qwen3-2B-base` | base | `21.1979%` | `73.3333%` | `18.8021%` | `53.3333%` | `76.4%` | `43.70%` | `14.57%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step100` | 100 | `22.2396%` | `73.3333%` | `20.6250%` | `63.3333%` | `80.4%` | `47.49%` | `15.83%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step200` | 200 | `20.2083%` | `66.6667%` | `18.2813%` | `66.6667%` | `81.2%` | `45.21%` | `15.07%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step300` | 300 | `18.7500%` | `76.6667%` | `16.4583%` | `63.3333%` | `76.6%` | `52.98%` | `17.66%` |
| Qwen3-2B V12 | `ArcherCodeR-V12-Qwen3-2B-8A100-step400` | 400 | `15.8854%` | `60.0000%` | `15.4687%` | `60.0000%` | `74.8%` | `55.84%` | `18.61%` |
| Qwen3-2B V13 | `ArcherCodeR-V13-Qwen3-2B-5090Lian-step200` | 200 | `9.6354%` | `46.6667%` | `13.8021%` | `36.6667%` | `74.4%` | `20.43%` | `6.81%` |
| Qwen3-2B V13 | `V13-Qwen3-2B-GradSketch-step200` | 200 | `21.4063%` | `70.00%` | `17.5521%` | `50.00%` | `75.6%` | `pending` | `pending` |
| Qwen3-2B V13 | `V13-Qwen3-2B-GradSketch-step300` | 300 | `17.3437%` | `66.67%` | `14.1146%` | `56.67%` | `74.0%` | `pending` | `pending` |
| Qwen3-2B V13grad quick | `V13grad-Qwen3-2B-step10` | 10 | `21.6667% avg@8` | `60.00% pass@8` | `21.6667% avg@8` | `40.00% pass@8` | `73.0%` | `pending` | `pending` |
| Qwen3-2B V13grad quick | `V13grad-Qwen3-2B-step100` | 100 | `25.4167% avg@8` | `60.00% pass@8` | `19.1667% avg@8` | `40.00% pass@8` | `77.2%` | `44.87%` | `14.96%` |

Notes:

- V13 GradSketch AIME values use the fair 32k retest. Earlier 8k AIME25 values are retained only as diagnostics in `results/eval_result_log_1_5B.md`.
- V13grad step10/step100 AIME values are quick 8-run checks (`avg@8/pass@8`), not full `avg@64/pass@64`.
- V14 Qwen2.5-1.5B step50 exploratory JSON outputs were also backfilled into the detailed log, but are not included in the cross-model summary because multiple debug protocols exist for the same step.

## 2026-05-19 Latest Backfill

Small CSV backups are stored under:

```text
results/latest_20260519/
```

### Arena-Hard Local 32B Judge

| Model | Judge | hard_prompt | creative_writing | overall | Used rows | Token usage |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `ArcherCodeR-V13-Qwen3-2B-5090Lian-step200` | `Qwen2.5-32B-Instruct` | `8.071%` | `11.021%` | `9.126%` | `745/750` | `11,466,526` |
| `Qwen3-2B-base` | `Qwen2.5-32B-Instruct` | `10.046%` | `18.289%` | `12.612%` | `746/750` | `8,439,059` |
| `V13grad-Qwen3-2B-step10` | `Qwen2.5-32B-Instruct` | `11.033%` | `18.812%` | `13.635%` | `743/750` | `8,326,465` |
| `V13grad-Qwen3-2B-step100` | `Qwen2.5-32B-Instruct` | `11.932%` | `17.030%` | `13.653%` | `746/750` | `7,884,054` |
| `V15-Qwen3-2B-step100` | `Qwen2.5-32B-Instruct` | `13.062%` | `26.775%` | `17.587%` | `744/750` | `8,038,896` |

V15 step500 is not recorded as a valid score: `/zhdd/home/tjshen/260415_ArcherA100/arena_hard_v15_step500_20260519` points to `global_step_500_merged` in logs, but the saved answer/judgment files are byte-identical to `V15-Qwen3-2B-step100`.

### V14 Round6 Qwen2.5-1.5B

| Model | Step | Math500 pass@1 | AIME24 avg@64 | AIME24 pass@64 | AIME25 avg@64 | AIME25 pass@64 | LCB total | LCB mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `V14-R6-Qwen25-1_5B-step50` | `50` | `46.8%` | `1.7188%` | `26.6667%` | `0.7292%` | `23.3333%` | `50.72%` | `16.91%` |
| `V14-R6-Qwen25-1_5B-step100` | `100` | `50.2%` | `2.1875%` | `26.6667%` | `0.4688%` | `20.0000%` | `47.40%` | `15.80%` |
| `V14-R6-Qwen25-1_5B-step150` | `150` | `48.0%` | `2.0833%` | `23.3333%` | `0.7292%` | `23.3333%` | `47.09%` | `15.70%` |
| `V14-R6-Qwen25-1_5B-step200` | `200` | `49.0%` | `2.3958%` | `36.6667%` | `0.5208%` | `13.3333%` | `53.90%` | `17.97%` |

V13 GradSketch step200 retry on 2026-05-19 did not produce a new promoted metric: the AIME retry failed on occupied GPU memory and the newer LCB run had predictions but no final numeric summary at scan time.

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
