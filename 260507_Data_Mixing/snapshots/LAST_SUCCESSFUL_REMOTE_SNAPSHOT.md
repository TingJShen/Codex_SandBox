# Last Successful Remote Snapshot

Snapshot time:

```text
2026-05-07 06:54 UTC
2026-05-07 14:54 Asia/Shanghai
```

This is the latest verified remote state before subsequent SSH attempts were reset by the gateway.

## Qwen3 P1

Running process:

```text
4078974 S 10:02 /usr/bin/time -v -o /zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1/logs/gen_answer_ArcherCodeR-V12-Qwen3-2B-8A100-step100.time.log python gen_answer.py --config-file config/gen_answer_config_ArcherCodeR-V12-Qwen3-2B-8A100-step100.yaml --endpoint-file config/api_config_ArcherCodeR-V12-Qwen3-2B-8A100-step100.yaml
```

Answer counts:

```text
Qwen3-2B-base.jsonl                                      750
ArcherCodeR-V12-Qwen3-2B-8A100-step100.jsonl             190
o3-mini-2025-01-31.jsonl                                 750
gemini-2.0-flash-001.jsonl                               748
```

Driver tail:

```text
[Thu May  7 05:54:44 AM UTC 2026] START_ANSWER model=Qwen3-2B-base temp=0.6 path=/zhdd/home/tjshen/260415_ArcherA100/model_overlays/Qwen3-2B_with_generation_config
[Thu May  7 05:54:44 AM UTC 2026] answer_server_pid=3986745 gpu=0 port=9961
[Thu May  7 06:43:32 AM UTC 2026] START_ANSWER model=ArcherCodeR-V12-Qwen3-2B-8A100-step100 temp=0.6 path=/zhdd/home/tjshen/260415_ArcherA100/qwen3_2b_eval_models/ArcherCodeR-V12-Qwen3-2B-8A100-step100-merged
[Thu May  7 06:43:32 AM UTC 2026] answer_server_pid=4076385 gpu=0 port=9961
```

## V11 P2

Running process:

```text
1760060 S 06:53 /usr/bin/time -v -o /zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507/logs/gen_answer_ArcherCodeR-V11-step560-merged.time.log python gen_answer.py --config-file config/gen_answer_config_ArcherCodeR-V11-step560-merged.yaml --endpoint-file config/api_config_ArcherCodeR-V11-step560-merged.yaml
```

Answer counts:

```text
ArcherCodeR-V11-step80-merged.jsonl                      750
ArcherCodeR-V11-step160-merged.jsonl                     750
ArcherCodeR-V11-step320-merged.jsonl                     750
ArcherCodeR-V11-step400-merged.jsonl                     750
ArcherCodeR-V11-step480-merged.jsonl                     750
ArcherCodeR-V11-step560-merged.jsonl                     637
```

Driver tail:

```text
[Thu May  7 06:15:23 AM UTC 2026] START_ANSWER model=ArcherCodeR-V11-step320-merged temp=0.6 path=/zhdd/home/tjshen/260415_ArcherA100/v11/output_A100/ArcherCodeR-V11-8A100/full_8a100_gpus2_7_bsz8_save80_v11_20260415/global_step_320_merged
[Thu May  7 06:24:57 AM UTC 2026] START_ANSWER model=ArcherCodeR-V11-step400-merged temp=0.6 path=/zhdd/home/tjshen/260415_ArcherA100/v11/output_A100/ArcherCodeR-V11-8A100/full_8a100_gpus2_7_bsz8_save80_v11_20260415/global_step_400_merged
[Thu May  7 06:35:34 AM UTC 2026] START_ANSWER model=ArcherCodeR-V11-step480-merged temp=0.6 path=/zhdd/home/tjshen/260415_ArcherA100/v11/output_A100/ArcherCodeR-V11-8A100/full_8a100_gpus2_7_bsz8_save80_v11_20260415/global_step_480_merged
[Thu May  7 06:47:07 AM UTC 2026] START_ANSWER model=ArcherCodeR-V11-step560-merged temp=0.6 path=/zhdd/home/tjshen/260415_ArcherA100/v11/output_A100/ArcherCodeR-V11-8A100/full_8a100_gpus2_7_bsz8_save80_v11_20260415/global_step_560_merged
```

## Judge Watchers

Processes:

```text
92541 S 01:06:06 bash /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_judge_priority_20260507.sh
110531 S 01:00:01 bash /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_judge_priority_20260507.sh
```

Qwen3 watcher tail:

```text
[Thu May  7 06:44:42 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V12-Qwen3-2B-8A100-step100 count=0
[Thu May  7 06:46:42 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V12-Qwen3-2B-8A100-step100 count=38
[Thu May  7 06:48:42 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V12-Qwen3-2B-8A100-step100 count=69
[Thu May  7 06:50:42 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V12-Qwen3-2B-8A100-step100 count=108
[Thu May  7 06:52:42 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V12-Qwen3-2B-8A100-step100 count=144
```

V11 watcher tail:

```text
[Thu May  7 06:46:39 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V11-step480-merged count=747
[Thu May  7 06:48:39 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V11-step560-merged count=85
[Thu May  7 06:50:39 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V11-step560-merged count=285
[Thu May  7 06:52:39 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V11-step560-merged count=527
[Thu May  7 06:54:39 AM UTC 2026] WAIT_ANSWERS model=ArcherCodeR-V11-step560-merged count=636
```

A100 judge GPU memory:

```text
GPU4: 68902 MiB / 81920 MiB
```
