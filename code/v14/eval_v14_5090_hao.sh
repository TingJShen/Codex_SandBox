#!/bin/bash
set -euo pipefail

BASE_DIR=/zhdd/home/tjshen/260415_ArcherA100
V14_DIR="${BASE_DIR}/v14"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <checkpoint_step> [gpu_id]"
    echo "Example: $0 50 0"
    exit 2
fi

STEP=$1
GPU_ID=${2:-0}

TRAIN_OUTPUT=$(ls -d ${V14_DIR}/output_5090_Hao/ArcherCodeR-V14-Qwen25-1_5B-5090Hao/train_v14_* 2>/dev/null | tail -1)
if [ -z "${TRAIN_OUTPUT}" ]; then
    echo "ERROR: No training output directory found"
    exit 1
fi

CKPT_DIR="${TRAIN_OUTPUT}/global_step_${STEP}"
MERGED_DIR="${CKPT_DIR}_merged"

if [ ! -d "${CKPT_DIR}" ]; then
    echo "ERROR: Checkpoint not found: ${CKPT_DIR}"
    exit 1
fi

echo "=== Step 1: Merge checkpoint ==="
if [ -d "${MERGED_DIR}" ] && [ -f "${MERGED_DIR}/config.json" ]; then
    echo "Merged model already exists: ${MERGED_DIR}"
else
    cd "${V14_DIR}"
    source /home/tjshen/miniconda3/bin/activate llama2_vllm
    bash tools/model_merge.sh "${CKPT_DIR}"
    echo "Merged to: ${MERGED_DIR}"
fi

echo "=== Step 2: Run Math500 eval (pass@1) ==="
EVAL_DIR="${V14_DIR}/eval_results/step_${STEP}"
mkdir -p "${EVAL_DIR}"

source /home/tjshen/miniconda3/bin/activate llama2_vllm

EVAL_PORT=9870
VLLM_PID=""

cleanup() {
    if [ -n "${VLLM_PID}" ] && kill -0 "${VLLM_PID}" 2>/dev/null; then
        kill "${VLLM_PID}" 2>/dev/null || true
        wait "${VLLM_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "Starting vLLM server on GPU ${GPU_ID}..."
CUDA_VISIBLE_DEVICES=${GPU_ID} python -m vllm.entrypoints.openai.api_server \
    --model "${MERGED_DIR}" \
    --port ${EVAL_PORT} \
    --dtype bfloat16 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.85 \
    --enforce-eager \
    --disable-log-requests \
    > "${EVAL_DIR}/vllm_server.log" 2>&1 &
VLLM_PID=$!

echo "Waiting for vLLM server to start..."
for i in $(seq 1 120); do
    if curl -s http://localhost:${EVAL_PORT}/health > /dev/null 2>&1; then
        echo "vLLM server ready after ${i}s"
        break
    fi
    if ! kill -0 "${VLLM_PID}" 2>/dev/null; then
        echo "ERROR: vLLM server died. Check ${EVAL_DIR}/vllm_server.log"
        exit 1
    fi
    sleep 1
done

if ! curl -s http://localhost:${EVAL_PORT}/health > /dev/null 2>&1; then
    echo "ERROR: vLLM server failed to start within 120s"
    exit 1
fi

echo "Running math500 evaluation..."
python "${V14_DIR}/tools/eval_math.py" \
    --api-base "http://localhost:${EVAL_PORT}/v1" \
    --model "${MERGED_DIR}" \
    --dataset math500 \
    --output "${EVAL_DIR}/math500_results.json" \
    2>&1 | tee "${EVAL_DIR}/math500_eval.log"

echo "Running AIME24 evaluation..."
python "${V14_DIR}/tools/eval_math.py" \
    --api-base "http://localhost:${EVAL_PORT}/v1" \
    --model "${MERGED_DIR}" \
    --dataset aime24 \
    --n-samples 64 \
    --output "${EVAL_DIR}/aime24_results.json" \
    2>&1 | tee "${EVAL_DIR}/aime24_eval.log"

echo "Running AIME25 evaluation..."
python "${V14_DIR}/tools/eval_math.py" \
    --api-base "http://localhost:${EVAL_PORT}/v1" \
    --model "${MERGED_DIR}" \
    --dataset aime25 \
    --n-samples 64 \
    --output "${EVAL_DIR}/aime25_results.json" \
    2>&1 | tee "${EVAL_DIR}/aime25_eval.log"

echo ""
echo "=== Evaluation Complete ==="
echo "Results in: ${EVAL_DIR}"
echo ""
cat "${EVAL_DIR}/math500_results.json" 2>/dev/null | python -c "import json,sys; d=json.load(sys.stdin); print(f'Math500 pass@1: {d.get(\"accuracy\", \"N/A\")}')" 2>/dev/null || true
cat "${EVAL_DIR}/aime24_results.json" 2>/dev/null | python -c "import json,sys; d=json.load(sys.stdin); print(f'AIME24 avg@64: {d.get(\"avg_accuracy\", \"N/A\")}')" 2>/dev/null || true
cat "${EVAL_DIR}/aime25_results.json" 2>/dev/null | python -c "import json,sys; d=json.load(sys.stdin); print(f'AIME25 avg@64: {d.get(\"avg_accuracy\", \"N/A\")}')" 2>/dev/null || true
