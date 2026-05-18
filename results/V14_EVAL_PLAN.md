# V14 Qwen2.5-1.5B Evaluation Plan

Created: 2026-05-18

## Evaluation Matrix

### Checkpoints to Evaluate

| Checkpoint | Round | Merged | Math500 | AIME24 avg@64 | AIME25 avg@64 | Status |
|---|---|---|---|---|---|---|
| base_model_v2 | — | — | 46.8% | — | — | Done |
| Round2 step50 | R2 | Yes | 48.8% | — | — | Done |
| Round5 step50 | R5 | Yes | 38.8%* | 2.60%* | 0.36%* | Done (4k ctx, unfair) |
| **Round6 step50** | R6 | No | — | — | — | Needs merge |
| **Round6 step100** | R6 | Yes | **50.2%** | **running** | **running** | In progress |
| **Round6 step150** | R6 | No | — | — | — | Needs merge |
| **Round6 step200** | R6 | Yes | — | — | — | Pending |

`*` = evaluated with max_tokens=4096 (unfair, model reasoning truncated)

### Baselines (from eval_result_log_1_5B.md)

| Model | Math500 | AIME24 avg@64 | AIME25 avg@64 |
|---|---|---|---|
| Qwen2.5-1.5B-Instruct | 55.8% | 2.71% | 0.68% |
| V11 best (step400) | 56.2% | 2.97% | 0.68% |
| V12 best (step200) | 59.0% | 3.13% | 1.09% |

### Priority Order

1. **Round6 step100** — currently running (Math500 done, AIME in progress)
2. **Round6 step200** — already merged, highest step count, most likely best result
3. **Round6 step150** — needs merge, intermediate checkpoint
4. **Round6 step50** — needs merge, early checkpoint

## Execution Plan

### Phase 1: Round6 step100 (IN PROGRESS)

- Server: 5090_Hao GPU 0
- vLLM config: `--attention-backend FLASHINFER --max-model-len 32768 --gpu-memory-utilization 0.85 --enforce-eager`
- Environment: `CUDA_HOME=/usr/local/cuda-12.9`, `no_proxy=localhost`
- [x] Math500 pass@1: **50.2%** (500 problems, 32k context)
- [ ] AIME25 avg@64: running (30 problems x 64 samples)
- [ ] AIME24 avg@64: queued after AIME25

ETA: ~6-12 hours total for AIME evaluations

### Phase 2: Round6 step200

After Phase 1 completes:
1. Keep vLLM server running (same GPU)
2. Swap model to `global_step_200_merged`
3. Run Math500 + AIME25 + AIME24

### Phase 3: Round6 step50 & step150

1. Merge checkpoints: `bash tools/model_merge.sh <ckpt_dir>`
2. Evaluate sequentially on same GPU

## Server Configuration (5090_Hao)

### Critical Settings for RTX 5090

```bash
# MUST use FlashInfer (vLLM bundled FlashAttn2 PTX incompatible with sm_120)
--attention-backend FLASHINFER

# MUST set CUDA 12.9 for JIT compilation
CUDA_HOME=/usr/local/cuda-12.9
PATH="/usr/local/cuda-12.9/bin:$PATH"

# MUST bypass HTTP proxy for localhost
no_proxy=localhost,127.0.0.1
http_proxy=""
https_proxy=""

# Fresh kernel caches (avoid stale compilations)
FLASHINFER_CACHE_DIR=/tmp/flashinfer_eval_<job>
FLASHINFER_JIT_CACHE_DIR=/tmp/flashinfer_eval_<job>
```

### Full Launch Command

```bash
source /home/tjshen/miniconda3/bin/activate llama2_vllm
nohup env \
  CUDA_VISIBLE_DEVICES=<gpu_id> \
  CUDA_DEVICE_ORDER=PCI_BUS_ID \
  CUDA_HOME=/usr/local/cuda-12.9 \
  PATH="/usr/local/cuda-12.9/bin:$PATH" \
  VLLM_ATTENTION_BACKEND=FLASHINFER \
  FLASHINFER_CACHE_DIR=/tmp/flashinfer_eval_<job> \
  FLASHINFER_JIT_CACHE_DIR=/tmp/flashinfer_eval_<job> \
  no_proxy=localhost,127.0.0.1 \
  http_proxy="" \
  https_proxy="" \
  python -m vllm.entrypoints.openai.api_server \
    --model <merged_model_path> \
    --port 9871 \
    --dtype bfloat16 \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.85 \
    --enforce-eager \
    --tensor-parallel-size 1 \
    --attention-backend FLASHINFER \
    --max-num-seqs 8 \
  > <log_path> 2>&1 &
```

### Eval Command

```bash
export no_proxy=localhost,127.0.0.1
export http_proxy=""
export https_proxy=""

# Math500 pass@1
python tools/eval_math.py \
  --api-base http://localhost:9871/v1 \
  --model <model_path> \
  --dataset math500 \
  --output <output.json> \
  --parallel 8 \
  --max-tokens 30000

# AIME avg@64
python tools/eval_math.py \
  --api-base http://localhost:9871/v1 \
  --model <model_path> \
  --dataset aime25 \
  --n-samples 64 \
  --output <output.json> \
  --parallel 4 \
  --max-tokens 30000
```

## Known Issues & Fixes

| Issue | Root Cause | Fix |
|---|---|---|
| 502 Bad Gateway | HTTP proxy intercepts localhost | `no_proxy=localhost,127.0.0.1` |
| CUDA PTX unsupported toolchain | vLLM FlashAttn2 C ext incompatible with sm_120 | `--attention-backend FLASHINFER` |
| max_tokens validation error | max_tokens >= max_model_len leaves no room for prompt | Use max_tokens=30000 with max_model_len=32768 |
| OOM on 5090 | gpu_memory_utilization too high with other processes | Use 0.85, check GPU is free first |

## GPU Resource Availability (5090_Hao, as of 2026-05-18)

| GPU | Memory Used | Available | Notes |
|---|---|---|---|
| 0 | 28.4 GiB | No | Running step100 eval |
| 1 | 31.0 GiB | No | Other process |
| 2 | 31.0 GiB | No | Other process |
| 3 | 31.0 GiB | No | Other process |
| 4 | 2 MiB | Yes | Free |
| 5 | 31.0 GiB | No | Other process |
| 6 | 2 MiB | Yes | Free |
| 7 | 2 MiB | Yes | Free |
