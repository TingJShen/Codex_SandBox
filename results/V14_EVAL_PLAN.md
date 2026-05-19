# V14 Qwen2.5-1.5B Evaluation Plan

Created: 2026-05-18

## Evaluation Matrix

### Checkpoints to Evaluate

| Checkpoint | Round | Merged | Math500 pass@1 | AIME24 avg@64 | AIME25 avg@64 | Status |
|---|---|---|---|---|---|---|
| base_model_v2 | — | — | 46.8% | — | — | Done |
| Round2 step50 | R2 | Yes | 48.8% | — | — | Done |
| Round5 step50 | R5 | Yes | 38.8%* | 2.60%* | 0.36%* | Done (4k ctx, unfair) |
| Round6 step50 | R6 | Yes | 46.8% | 1.7188% | 0.7292% | Done |
| Round6 step100 | R6 | Yes | 50.2% | 2.1875% | 0.4688% | Done |
| Round6 step150 | R6 | Yes | 48.0% | 2.0833% | 0.7292% | Done |
| Round6 step200 | R6 | Yes | 49.0% | 2.3958% | 0.5208% | Done |

`*` = evaluated with max_tokens=4096 (unfair, model reasoning truncated)

### Round6 Final Results Summary (2026-05-18, 32k context)

| Checkpoint | Math500 pass@1 | AIME24 avg@64 | AIME24 pass@64 | AIME25 avg@64 | AIME25 pass@64 |
|---|---|---|---|---|---|
| step50 | 46.8% | 1.7188% | 26.6667% | 0.7292% | 23.3333% |
| step100 | **50.2%** | 2.1875% | 26.6667% | 0.4688% | 20.0000% |
| step150 | 48.0% | 2.0833% | 23.3333% | 0.7292% | 23.3333% |
| step200 | 49.0% | **2.3958%** | **36.6667%** | 0.5208% | 13.3333% |

**Best checkpoint**: step100 (best Math500), step200 (best AIME24)

**vs Baselines**:
- Qwen2.5-1.5B-Instruct: Math500=55.8%, AIME24=2.71%, AIME25=0.68%
- V12 best (step200): Math500=59.0%, AIME24=3.13%, AIME25=1.09%
- V14 Round6 best: Math500=50.2%, AIME24=2.40%, AIME25=0.73%
- Gap remains: Math500 -5.6pp, AIME24 -0.31pp, AIME25 +0.05pp vs Instruct baseline

### Round6 LCB (LiveCodeBench) Results (2026-05-19, 32k context)

| Checkpoint | code_generation pass@1 | code_execution pass@1 | test_output pass@1 | LCB total | LCB mean |
|---|---|---|---|---|---|
| step50 | 14.75% | 29.23% | 5.66% | 49.64% | 16.55% |
| step100 | 15.00% | 29.23% | 3.17% | 47.40% | 15.80% |
| step150 | 14.50% | 30.06% | 2.94% | 47.50% | 15.83% |
| step200 | **15.50%** | **30.48%** | **7.92%** | **53.90%** | **17.97%** |

**Best checkpoint**: step200 (best across all LCB metrics)

**vs Baselines (LCB)**:
- Qwen2.5-1.5B-Instruct: code_gen=0.00%, code_exec=30.90%, test_output=3.85%, total=34.75%, mean=11.58%
- V11 best (step400): code_gen=16.00%, code_exec=30.48%, test_output=0.23%, total=46.71%, mean=15.57%
- V12 best (step200): code_gen=16.25%, code_exec=28.81%, test_output=5.20%, total=50.26%, mean=16.75%
- **V14 Round6 best (step200): code_gen=15.50%, code_exec=30.48%, test_output=7.92%, total=53.90%, mean=17.97%**
- V14 Round6 step200 beats V12 best: total +3.64pp, mean +1.22pp
- V14 Round6 step200 beats Instruct: total +19.15pp, mean +6.39pp

### Baselines (from eval_result_log_1_5B.md)

| Model | Math500 | AIME24 avg@64 | AIME25 avg@64 | LCB total | LCB mean |
|---|---|---|---|---|---|
| Qwen2.5-1.5B-Instruct | 55.8% | 2.71% | 0.68% | 34.75% | 11.58% |
| V11 best (step400) | 56.2% | 2.97% | 0.68% | 46.71% | 15.57% |
| V12 best (step200) | 59.0% | 3.13% | 1.09% | 50.26% | 16.75% |

### Priority Order

All evaluations completed 2026-05-18 ~16:40 UTC.

## Execution Plan

### All 4 Checkpoints Running in Parallel (2026-05-18 12:16 UTC)

| Checkpoint | Server | GPU | Port | Current Task | Started |
|---|---|---|---|---|---|
| step100 | 5090_Hao | 0 | 9871 | AIME24 avg@64 | 11:15 UTC |
| step200 | 5090_Lian | 1 | 9872 | Math500 pass@1 | 12:10 UTC |
| step50 | 5090_Lian | 0 | 9873 | Math500 pass@1 | 12:16 UTC |
| step150 | 5090_Lian | 4 | 9874 | Math500 pass@1 | 12:16 UTC |

Each eval pipeline: Math500 (~15min) → AIME25@64 (~90min) → AIME24@64 (~90min)

Step50 and step150 were merged at 12:15 UTC (CPU-only, ~40s each).

**Estimated total completion: ~15:30 UTC (step100 earliest, ~12:40 UTC)**

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

## GPU Resource Availability (as of 2026-05-18 12:16 UTC)

### 5090_Hao (8× RTX 5090 32GB)

| GPU | Used | Process | Notes |
|---|---|---|---|
| 0 | 28.4 GiB | Our vLLM (step100) | AIME24 eval |
| 1 | 31.0 GiB | Qwen2.5-32B TP0 | Arena eval |
| 2 | 31.0 GiB | Qwen2.5-32B TP1 | Arena eval |
| 3 | 31.0 GiB | Qwen2.5-32B TP2 | Arena eval |
| 4 | 23.2 GiB | jqzhang collect_projections | Data selection |
| 5 | 31.0 GiB | Qwen2.5-32B TP3 | Arena eval |
| 6 | 23.2 GiB | jqzhang collect_projections | Data selection |
| 7 | 23.2 GiB | jqzhang collect_projections | Data selection |

### 5090_Lian (6× RTX 5090 32GB)

| GPU | Used | Process | Notes |
|---|---|---|---|
| 0 | ~28 GiB | Our vLLM (step50) | Math → AIME eval |
| 1 | ~28 GiB | Our vLLM (step200) | Math → AIME eval |
| 2 | 17.1 GiB | Other process | Busy |
| 3 | 15.5 GiB | Other process | Busy |
| 4 | ~28 GiB | Our vLLM (step150) | Math → AIME eval |
| 5 | 15.8 GiB | Other process | Busy |
