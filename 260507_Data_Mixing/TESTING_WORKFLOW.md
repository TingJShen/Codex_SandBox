# Testing Workflow

## Goal

Fill missing evaluations for ArcherCodeR V11/V12 and Qwen3-2B Data Mixing experiments, especially Arena-Hard gaps, while preserving existing training/evaluation code and keeping all remote artifacts under:

```text
/zhdd/home/tjshen/260415_ArcherA100
```

## Evaluation Priority Used on 2026-05-07

1. P1: Qwen3-2B base plus selected Qwen3-2B V12 merged checkpoints needed Arena-Hard because math/code had already been recorded but Arena was missing.
2. P2: V11 checkpoints other than step240 needed Arena-Hard because step240 already had Arena and all V11 math/code were already in the local result log.
3. Lower priority: later raw Qwen3-2B 5090_Lian step100 checkpoints existed, but many were not merged or recorded in the result table. They were not launched before the higher-priority listed models.

## Servers and Environments

| Role | Server | GPU | Environment |
| --- | --- | --- | --- |
| Qwen3 answer generation | `5090_Hao` | GPU0 | `5090_opencompass` |
| V11 answer generation | `5090_Lian` | GPU1 | `5090_opencompass` |
| Local 32B judge watcher | `8A100` | GPU4 | `5090_opencompass` |

Judge model:

```text
/zhdd/models/Qwen2.5-32B-Instruct
```

## Created Scripts

Remote script directory:

```text
/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts
```

Archived copies in this repository:

```text
scripts/arena_answers_priority_20260507.sh
scripts/arena_judge_priority_20260507.sh
scripts/arena_token_usage.py
scripts/arena_tolerant_summary.py
manifests/manifest_qwen3_arena_p1_20260507.tsv
manifests/manifest_v11_arena_p2_20260507.tsv
```

## Qwen3 Arena P1 Launch

Work directory:

```text
/zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1
```

Answer generation launch:

```bash
ssh 5090_Hao 'mkdir -p /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507; RUN_ID=arena_priority_qwen3_p1_20260507_retry1 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_qwen3_arena_p1_20260507.tsv ANSWER_GPU=0 ANSWER_PORT=9961 ANSWER_GPU_MEMORY_UTILIZATION=0.55 USE_QWEN3_MM_FIX=1 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_answers_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/qwen3_p1_answers_retry1_5090hao_gpu0.out 2>&1 &'
```

Judge watcher launch:

```bash
ssh 8A100 'mkdir -p /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507; RUN_ID=arena_priority_qwen3_p1_20260507_retry1 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_qwen3_p1_20260507_retry1 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_qwen3_arena_p1_20260507.tsv JUDGE_GPU=4 JUDGE_PORT=9963 JUDGE_MAX_USED_MEM_MIB=4096 GPU_POLL_INTERVAL_SEC=120 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_judge_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/qwen3_p1_judge_retry1_8a100_gpu4.out 2>&1 &'
```

### Qwen3 Failure and Fix

Initial Qwen3 Arena launch failed when vLLM resolved the model as:

```text
Qwen3_5ForConditionalGeneration
model_type=qwen3_5
vision_config present
```

The server entered the multimodal/VL encoder path and hit:

```text
CUDA error: the provided PTX was compiled with an unsupported toolchain
cudaErrorUnsupportedPtxVersion
```

Root cause:

```text
5090 environment used a FlashAttention/PTX path incompatible with the Qwen3.5/VL-style multimodal encoder path.
```

Fix applied only in the standalone Arena answer script when `USE_QWEN3_MM_FIX=1`:

```bash
export ARCHER_QWEN35_SOURCE_MODELS_DIR="${ROOT}/qwen3_pydeps/transformers_qwen3_20260420_min2/transformers/models"
export PYTHONPATH="${QWEN35_SHIM}:${OVERLAY}:${PYTHONPATH:-}"
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export M3EVAL_ATTENTION_BACKEND=FLASHINFER
export M3EVAL_MM_ENCODER_ATTN_BACKEND=TORCH_SDPA
export M3EVAL_SKIP_MM_PROFILING=1
```

vLLM server flags added:

```bash
--mm-encoder-attn-backend TORCH_SDPA
--skip-mm-profiling
```

Verification evidence from server log:

```text
Using AttentionBackendEnum.TORCH_SDPA for vit attention
Using AttentionBackendEnum.TORCH_SDPA for MMEncoderAttention
GET /health HTTP/1.1 200 OK
```

## V11 Arena P2 Launch

Work directory:

```text
/zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507
```

Answer generation launch:

```bash
ssh 5090_Lian 'mkdir -p /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507; RUN_ID=arena_priority_v11_p2_20260507 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_v11_arena_p2_20260507.tsv ANSWER_GPU=1 ANSWER_PORT=9962 ANSWER_GPU_MEMORY_UTILIZATION=0.55 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_answers_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/v11_p2_answers_5090lian_gpu1.out 2>&1 &'
```

Judge watcher launch:

```bash
ssh 8A100 'RUN_ID=arena_priority_v11_p2_20260507 WORK=/zhdd/home/tjshen/260415_ArcherA100/arena_priority_v11_p2_20260507 MANIFEST=/zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/manifest_v11_arena_p2_20260507.tsv JUDGE_GPU=4 JUDGE_PORT=9964 JUDGE_MAX_USED_MEM_MIB=4096 GPU_POLL_INTERVAL_SEC=120 nohup /zhdd/home/tjshen/260415_ArcherA100/arena_hard_scripts/arena_judge_priority_20260507.sh > /zhdd/home/tjshen/260415_ArcherA100/diag_arena_priority_20260507/v11_p2_judge_8a100_gpu4.out 2>&1 &'
```

### V11 Failure and Fix

V11 step80 initially stopped at `749/750` answers. The model server had served responses normally; the failure was in post-processing:

```text
requests.exceptions.HTTPError: 404 Client Error
url: https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken
```

Root cause:

```text
tiktoken.encoding_for_model("gpt-4o") attempted to download o200k_base.tiktoken at runtime. The remote server/network returned 404, causing the final worker future to fail.
```

Fix:

```bash
export TIKTOKEN_CACHE_DIR="${ROOT}/shared_cache/tiktoken"
```

The cache key for the URL is:

```text
fb374d419588a4632f3f557e76b4b70aebbca790
```

The cached file SHA256 was verified as:

```text
446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
```

After this, V11 step80 resumed, reached `750/750`, and the driver automatically advanced to later V11 checkpoints.

## Judge Workflow

The judge script does not start immediately. It waits for every model in its manifest to have `750/750` answer rows, then waits for GPU memory to be below threshold:

```bash
JUDGE_MAX_USED_MEM_MIB=4096
GPU_POLL_INTERVAL_SEC=120
```

It also uses a directory lock:

```text
/zhdd/home/tjshen/260415_ArcherA100/locks/arena_judge_gpu4.lock
```

This avoids two local 32B judge jobs competing for the same A100 GPU.

## Output Products

For each Arena work directory:

```text
data/arena-hard-v2.0/model_answer/*.jsonl
data/arena-hard-v2.0/model_judgment/Qwen2.5-32B-Instruct/*.jsonl
arena_token_usage.csv
arena_tolerant_summary.csv
arena_tolerant_bad_labels.csv
logs/*.log
```

Large JSONL outputs are intentionally not archived in GitHub. Remote paths are recorded instead.
