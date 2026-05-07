# V13 Training Results and Status, 2026-05-07

## Summary

The V13 Qwen2.5-1.5B training path was verified to enter the new `sample_taylor_v13` trainer and sampler. The latest direct GPU0/GPU7 run reached V13 `step=1`, initialized fixed shadow anchors, computed target representations, sampled domain weights, and entered rollout/reward/update. It then failed during actor optimizer step because GPU0 was occupied by another user's large process.

No model checkpoint was produced by the failed `bsz64` GPU0/GPU7 run, because it failed before reaching the first save boundary.

Current action: a watcher is alive and waiting for GPU0 and GPU7 to both free at least 70000 MiB before launching the larger `bsz96/mini48/util0.70` run.

## Latest Direct Run

```text
Host: 8A100
Physical GPUs: 0,7
Experiment:
  train_8a100_v13_qwen25_1_5b_2gpu_gpus0_7_bsz64_mini32_util060_noexpand_save100_20260507_050620
Output:
  /zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu/ArcherCodeR-V13-Qwen25-1_5B-8A100/train_8a100_v13_qwen25_1_5b_2gpu_gpus0_7_bsz64_mini32_util060_noexpand_save100_20260507_050620
Train log:
  /zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu/ArcherCodeR-V13-Qwen25-1_5B-8A100/train_8a100_v13_qwen25_1_5b_2gpu_gpus0_7_bsz64_mini32_util060_noexpand_save100_20260507_050620/train.log
Ray address:
  127.0.0.1:6784
Runtime:
  /home/tjshen/t807b
Ray tmp:
  /home/tjshen/r807b
```

Parameters:

```text
TRAIN_PROMPT_BSZ=64
TRAIN_PROMPT_MINI_BSZ=32
ROLLOUT_GPU_MEMORY_UTILIZATION=0.60
DISABLE_PYTORCH_CUDA_ALLOC_CONF=1
TOTAL_TRAINING_STEPS=2000
SAVE_FREQ=100
DYNAMIC_METHOD=sample_taylor_v13
FULL_DATASET_EMBEDDING_BATCH_SIZE=4
SHADOW_ANCHOR_SIZE_PER_DOMAIN=128
CANDIDATE_MULTIPLIER=4
GRAD_PROJECTION_DIM=256
CURVATURE_REFRESH_FREQ=50
FULL_TRAIN_MAX_SAMPLES_PER_CATEGORY=4
FULL_TARGET_MAX_SAMPLES_PER_CATEGORY=4
```

Observed dataset loading:

```text
train dataset len: 18035
train filter dataset len: 17681
validation dataset len: 279
validation filter dataset len: 259
train dataloader size: 276
validation dataloader size: 1
```

Observed V13 sampler state:

```text
[V13] Fixed shadow anchors: {'general': 128, 'code': 128, 'math': 128}
SampleTaylorBatchSampler initialized:
  Categories: ['math', 'code', 'general']
  Samples per category: {'math': 5454, 'code': 4730, 'general': 7113}
  Batch size: 64
  Candidate multiplier: 4
[V13] step=1 weights={'math': 0.31904458701610566, 'code': 0.34183641225099565, 'general': 0.3391190007328987}
```

Failure:

```text
ray.exceptions.RayTaskError(OutOfMemoryError):
ray::WorkerDict.actor_rollout_update_actor()
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 90.00 MiB.
GPU 0 had only 74.25 MiB free.
The V13 worker had 16.13 GiB in use.
Another process, PID 4184880 / later PID 18645 under user jiahe, occupied about 62.98 GiB on GPU0.
```

Conclusion: this failure was caused by external GPU memory contention, not by the V13 sampler route failing. The run proved that the V13 training path enters the intended method, but it did not complete a saveable step.

## Attempt Table

| Time / phase | Host | GPUs | Main config | Result |
| --- | --- | --- | --- | --- |
| Earlier smoke | 8A100 | 0,4 | `bsz32`, `mini16`, `util0.40`, save every 100 | Reached step 4; stopped because requested GPUs changed to 0,7. |
| First GPU0/GPU7 attempt | 8A100 | 0,7 | Shared `/zhdd` Ray temp path | Failed due AF_UNIX path length greater than 107 bytes. |
| Short-path GPU0/GPU7 attempt | 8A100 | 0,7 | Shorter Ray path | Ray started but initialization was slow/stalled on shared runtime/cache. |
| Local runtime attempt | 8A100 | 0,7 | Local runtime and high 331xx ports | Ray startup timed out. |
| Known-port attempt | 8A100 | 0,7 | `RAY_PORT=6784` | Workers started but vLLM failed because PyTorch expandable segments were enabled. |
| No-expand attempt | 8A100 | 0,7 | `bsz64`, `mini32`, `util0.60`, `DISABLE_PYTORCH_CUDA_ALLOC_CONF=1` | Entered V13 `step=1`; failed at actor optimizer due external GPU0 memory occupation. |
| Current watcher | 8A100 | 0,7 | waits for both cards `>=70000 MiB` free, then launches `bsz96`, `mini48`, `util0.70` | Waiting; not launched at the last recorded snapshot. |

## Last Recorded GPU Contention Snapshot

At the last successful local check:

```text
GPU0 total used: about 63.1 GiB
GPU0 external process: user jiahe, about 63.1 GiB
GPU7 total used: about 58.1 GiB
GPU7 external process: user psjin, about 58.0 GiB
Our failed V13 Ray/worker processes had already exited.
```

Because the user explicitly requested GPU0 and GPU7, the safe response was not to steal or kill other users' jobs. The watcher waits until the cards are actually free.

## Current Watcher

```text
Watcher PID observed: 30215
Watcher directory:
  /zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu/_watch_gpus0_7_q25_bsz96_20260507_052806
Watcher log:
  /zhdd/home/tjshen/260415_ArcherA100/v13/output_8A100_2gpu/_watch_gpus0_7_q25_bsz96_20260507_052806/watcher.log
Launch threshold:
  GPU0 free >= 70000 MiB and GPU7 free >= 70000 MiB
```

Initial watcher state:

```text
[Thu May  7 05:28:06 AM UTC 2026] watcher started on young, waiting for GPU0 and GPU7 free >= 70000 MiB
WORK_DIR=/zhdd/home/tjshen/260415_ArcherA100/v13
SCRIPT=/zhdd/home/tjshen/260415_ArcherA100/v13/dynamic_train_v13_a100_smoke_bsz4_20step.sh
[Thu May  7 05:28:07 AM UTC 2026] gpu_state=0, 63111, 18042, 98;7, 58057, 23096, 38
```

Meaning: GPU0 had only 18042 MiB free and GPU7 had 23096 MiB free, so the watcher correctly did not launch.

## What Counts as Success Next

The next launch should only be considered successful after all of the following are true:

```text
1. The log contains "[V13] Using RayDAPOTrainerV13 with sample_taylor_v13 method".
2. The log contains fixed shadow anchors for math/code/general.
3. The log contains at least one "[V13] step=..." weight update.
4. The log passes actor update without OOM.
5. Training progress advances beyond step 1.
6. Checkpoint directories appear at save boundaries, starting from step100.
```
