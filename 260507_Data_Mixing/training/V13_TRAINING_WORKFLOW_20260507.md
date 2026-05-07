# V13 Training Workflow, 2026-05-07

## Scope

This document records the V13 training flow prepared from the V11 codebase and operated on the shared A100/5090 servers. The main live target in this archive is:

```text
Method: sample_taylor_v13
Base model: /zhdd/models/Qwen2.5-1.5B-Instruct
Reward model: /zhdd/home/tjshen/260413_Backup_model_resume_20260323_031320/Skywork-Reward-Llama-3.1-8B-v0.2
Dataset: /zhdd/home/tjshen/260415_ArcherA100/v13/data/train/Mix_AirRep_nonrepeated_sysprom.json
Target test files:
  math: /zhdd/home/tjshen/260415_ArcherA100/v13/data/test/AIME2025.json
  code: /zhdd/home/tjshen/260415_ArcherA100/v13/data/test/LCB.json
  general: /zhdd/home/tjshen/260415_ArcherA100/v13/data/test/Arena_question.json
```

The training output must stay under the V13 tree:

```text
/zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu
```

## V13 Code Layout

The V13 code is an independent copy and does not modify V11 in place.

```text
/zhdd/home/tjshen/260415_ArcherA100/v13
/home/tjshen/v13_run_q25_20260506_173125
```

The shared V13 tree is the canonical archive path. The `/home/tjshen/v13_run_q25_20260506_173125` copy was used as a faster local execution copy during earlier 8A100 tests. Both keep the package name `dapo`, so the training entry remains:

```text
python -m dapo.main_dapo
```

## V13 Method Parameters

The active V13 training path uses:

```text
trainer.dynamic_sampling.enable=True
trainer.dynamic_sampling.method=sample_taylor_v13
trainer.dynamic_sampling.update_freq=10
trainer.dynamic_sampling.min_weight=0.05
trainer.dynamic_sampling.use_inverse_improvement=True
trainer.dynamic_sampling.full_dataset_embedding_batch_size=4
trainer.dynamic_sampling.full_train_max_samples_per_category=4
trainer.dynamic_sampling.full_target_max_samples_per_category=4
trainer.dynamic_sampling.full_train_max_tokens=1024
trainer.dynamic_sampling.full_target_max_tokens=2048
trainer.dynamic_sampling.shadow_anchor_size_per_domain=128
trainer.dynamic_sampling.candidate_multiplier=4
trainer.dynamic_sampling.grad_projection_dim=256
trainer.dynamic_sampling.grad_projection_seed=20260506
trainer.dynamic_sampling.sample_softmax_temperature=0.7
trainer.dynamic_sampling.domain_softmax_temperature=1.0
trainer.dynamic_sampling.domain_min_weight=0.15
trainer.dynamic_sampling.learn_ema_decay=0.2
trainer.dynamic_sampling.curvature_refresh_freq=50
trainer.dynamic_sampling.sample_score_weights.target_rel=1.0
trainer.dynamic_sampling.sample_score_weights.align=1.0
trainer.dynamic_sampling.sample_score_weights.learn=0.5
trainer.dynamic_sampling.sample_score_weights.curv=0.5
trainer.dynamic_sampling.sample_score_weights.age=0.05
```

Important observed V13 initialization output:

```text
[V13] Fixed shadow anchors: {'general': 128, 'code': 128, 'math': 128}
SampleTaylorBatchSampler initialized:
  Categories: ['math', 'code', 'general']
  Samples per category: {'math': 5454, 'code': 4730, 'general': 7113}
  Batch size: 64
  Candidate multiplier: 4
[V13] step=1 weights={'math': 0.31904458701610566, 'code': 0.34183641225099565, 'general': 0.3391190007328987}
```

This confirms the `sample_taylor_v13` route entered the V13 trainer and built the sample-level Taylor sampler.

## Environment

The A100 training environment used:

```text
CONDA_ENV_NAME=llama2_vllm_copy
/home/tjshen/miniconda3/envs/llama2_vllm_copy
```

Important environment fix:

```text
DISABLE_PYTORCH_CUDA_ALLOC_CONF=1
```

Reason: the default launcher exports `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, but the vLLM memory pool rejects expandable segments with:

```text
AssertionError: Expandable segments are not compatible with memory pool.
```

Therefore every successful or future V13 launch should pass `DISABLE_PYTORCH_CUDA_ALLOC_CONF=1`.

## Operational Rules

These rules were followed during the remote work:

```text
Do not use rm.
Do not use /tmp.
Keep logs, scripts, Ray runtime, and caches under /zhdd/home/tjshen/260415_ArcherA100 when possible.
Do not kill other users' GPU processes.
When GPU cards are shared, decide by free memory, not utilization alone.
Prefer environment fixes before changing training code.
```

## 8A100 Launch History

### Earlier 0,4 smoke

An earlier 8A100 run on GPUs `0,4` used approximately:

```text
CUDA_VISIBLE_DEVICES=0,4
TRAIN_PROMPT_BSZ=32
TRAIN_PROMPT_MINI_BSZ=16
ROLLOUT_GPU_MEMORY_UTILIZATION=0.40
DISABLE_PYTORCH_CUDA_ALLOC_CONF=1
SAVE_FREQ=100
```

It reached training step 4. The run was stopped because the requested cards changed to `0,7`.

### GPU0/GPU7 preparation attempts

The GPU0/GPU7 sequence exposed several environment/runtime issues:

| Attempt | Parameters / setup | Result |
| --- | --- | --- |
| Long Ray temp path under `/zhdd` | `CUDA_VISIBLE_DEVICES=0,7` | Failed before training because AF_UNIX socket path exceeded the 107 byte limit. |
| Shorter shared Ray path | `CUDA_VISIBLE_DEVICES=0,7` | Ray started but initialization was slow/stalled on shared runtime/cache. |
| Local runtime with new high ports | local `/home/tjshen` runtime, 331xx ports | Ray node startup timed out. |
| Local runtime with known ports | `RAY_PORT=6784`, local runtime/cache | Reached workers but failed on vLLM expandable segments. |
| No-expand bsz64 run | `bsz64`, `mini32`, `util0.60`, `DISABLE_PYTORCH_CUDA_ALLOC_CONF=1` | Entered V13 `step=1`, then OOM during actor optimizer because another user's process occupied most of GPU0. |

## Current Intended Relaunch

Because GPU0 and GPU7 were later occupied by other users, the current safe plan is a background watcher. It only launches when both GPU0 and GPU7 have at least 70000 MiB free.

Planned launch:

```text
CUDA_VISIBLE_DEVICES=0,7
TRAIN_PROMPT_BSZ=96
TRAIN_PROMPT_MINI_BSZ=48
ROLLOUT_GPU_MEMORY_UTILIZATION=0.70
DISABLE_PYTORCH_CUDA_ALLOC_CONF=1
SAVE_FREQ=100
TOTAL_TRAINING_STEPS=2000
RAY_PORT=6787
RUNTIME_DIR=/zhdd/home/tjshen/260415_ArcherA100/t807d
RAY_TMPDIR=/zhdd/home/tjshen/260415_ArcherA100/r807d
```

Watcher path:

```text
/zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu/_watch_gpus0_7_q25_bsz96_20260507_052806/watcher.log
```

The reproducible watcher script is archived at:

```text
../scripts/train_v13_8a100_gpus0_7_wait_free_bsz96.sh
```
