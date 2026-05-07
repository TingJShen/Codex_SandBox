#!/usr/bin/env bash
set -euo pipefail

ROOT="/zhdd/home/tjshen/260415_ArcherA100"
PREV_WORK="${ROOT}/arena_hard_v12_400_500_local32b_5090_hao_flashinfer_20260421_030055"
SCRIPT_DIR="${ROOT}/arena_hard_scripts"

RUN_ID="${RUN_ID:-arena_priority_$(date +%Y%m%d_%H%M%S)}"
WORK="${WORK:-${ROOT}/${RUN_ID}}"
MANIFEST="${MANIFEST:?MANIFEST is required}"
ENV_NAME="${ENV_NAME:-5090_opencompass}"

ANSWER_GPU="${ANSWER_GPU:-0}"
ANSWER_PORT="${ANSWER_PORT:-9986}"
ANSWER_MAX_MODEL_LEN="${ANSWER_MAX_MODEL_LEN:-32768}"
ANSWER_MAX_TOKENS="${ANSWER_MAX_TOKENS:-8192}"
ANSWER_PARALLEL="${ANSWER_PARALLEL:-16}"
ANSWER_GPU_MEMORY_UTILIZATION="${ANSWER_GPU_MEMORY_UTILIZATION:-0.60}"
ANSWER_TEMPERATURE="${ANSWER_TEMPERATURE:-0.6}"

mkdir -p \
  "${WORK}/logs" \
  "${WORK}/config" \
  "${WORK}/scripts" \
  "${WORK}/data/arena-hard-v2.0/model_answer" \
  "${WORK}/data/arena-hard-v2.0/model_judgment" \
  "${WORK}/cache" \
  "${ROOT}/shared_cache/tiktoken" \
  "${ROOT}/t"

SHORT_TMP="${ROOT}/t/aa_${RUN_ID: -10}"
mkdir -p "${SHORT_TMP}"
export TMPDIR="${SHORT_TMP}"
export TEMP="${SHORT_TMP}"
export TMP="${SHORT_TMP}"
export XDG_CACHE_HOME="${WORK}/cache/xdg"
export HF_HOME="${WORK}/cache/hf"
export TRANSFORMERS_CACHE="${WORK}/cache/hf/transformers"
export TORCHINDUCTOR_CACHE_DIR="${WORK}/cache/torchinductor"
export TRITON_CACHE_DIR="${WORK}/cache/triton"
export VLLM_CACHE_ROOT="${WORK}/cache/vllm"
export TIKTOKEN_CACHE_DIR="${ROOT}/shared_cache/tiktoken"
export NO_PROXY="127.0.0.1,localhost,::1${NO_PROXY:+,${NO_PROXY}}"
export no_proxy="127.0.0.1,localhost,::1${no_proxy:+,${no_proxy}}"
export CUDA_DEVICE_ORDER="PCI_BUS_ID"

USE_QWEN3_MM_FIX="${USE_QWEN3_MM_FIX:-0}"
if [[ "${USE_QWEN3_MM_FIX}" == "1" ]]; then
  OVERLAY="${ROOT}/envs/archer_qwen3_vllm_torch210_overlay/python_packages"
  QWEN35_SHIM="${ROOT}/diag_5090_Hao_v12_qwen3_2b_20260421/qwen35_flashattn_shim"
  export ARCHER_QWEN35_SOURCE_MODELS_DIR="${ROOT}/qwen3_pydeps/transformers_qwen3_20260420_min2/transformers/models"
  export PYTHONPATH="${QWEN35_SHIM}:${OVERLAY}:${PYTHONPATH:-}"
  export VLLM_WORKER_MULTIPROC_METHOD="${VLLM_WORKER_MULTIPROC_METHOD:-spawn}"
  export M3EVAL_ATTENTION_BACKEND="${M3EVAL_ATTENTION_BACKEND:-FLASHINFER}"
  export M3EVAL_MM_ENCODER_ATTN_BACKEND="${M3EVAL_MM_ENCODER_ATTN_BACKEND:-TORCH_SDPA}"
  export M3EVAL_SKIP_MM_PROFILING="${M3EVAL_SKIP_MM_PROFILING:-1}"
fi

cp "${PREV_WORK}/gen_answer.py" "${WORK}/gen_answer.py"
cp "${PREV_WORK}/gen_judgment.py" "${WORK}/gen_judgment.py"
cp "${PREV_WORK}/show_result.py" "${WORK}/show_result.py"
cp -a "${PREV_WORK}/utils/." "${WORK}/utils"
cp "${SCRIPT_DIR}/arena_token_usage.py" "${WORK}/scripts/arena_token_usage.py"
cp "${SCRIPT_DIR}/arena_tolerant_summary.py" "${WORK}/scripts/arena_tolerant_summary.py"
cp "${PREV_WORK}/data/arena-hard-v2.0/question.jsonl" "${WORK}/data/arena-hard-v2.0/question.jsonl"

for baseline_answer in "o3-mini-2025-01-31" "gemini-2.0-flash-001"; do
  cp \
    "${PREV_WORK}/data/arena-hard-v2.0/model_answer/${baseline_answer}.jsonl" \
    "${WORK}/data/arena-hard-v2.0/model_answer/${baseline_answer}.jsonl"
done

cp "${MANIFEST}" "${WORK}/run_manifest.tsv"

source /home/tjshen/miniconda3/etc/profile.d/conda.sh
conda activate "${ENV_NAME}"

python - <<PY
from pathlib import Path
import yaml

work = Path("${WORK}")
work_config = work / "config"
for line in (work / "run_manifest.tsv").read_text(encoding="utf-8").splitlines()[1:]:
    if not line.strip():
        continue
    model, _model_path = line.split("\t", 1)
    safe = model.replace("/", "__")
    api_cfg = {
        model: {
            "model": model,
            "endpoints": [{"api_base": "http://127.0.0.1:${ANSWER_PORT}/v1", "api_key": "-"}],
            "api_type": "openai",
            "parallel": int("${ANSWER_PARALLEL}"),
            "max_tokens": int("${ANSWER_MAX_TOKENS}"),
            "temperature": float("${ANSWER_TEMPERATURE}"),
        },
    }
    gen_cfg = {"bench_name": "arena-hard-v2.0", "model_list": [model]}
    (work_config / f"api_config_{safe}.yaml").write_text(
        yaml.safe_dump(api_cfg, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (work_config / f"gen_answer_config_{safe}.yaml").write_text(
        yaml.safe_dump(gen_cfg, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
PY

ANSWER_SERVER_PID=""

stop_pid() {
  local pid="$1"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  fi
}

cleanup_server() {
  stop_pid "${ANSWER_SERVER_PID}"
}
trap cleanup_server EXIT

wait_for_server() {
  local port="$1"
  local pid="$2"
  local log_file="$3"
  for _ in $(seq 1 360); do
    if curl --noproxy "*" -fsS "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
      return 0
    fi
    if ! kill -0 "${pid}" 2>/dev/null; then
      echo "Server exited early on port ${port}. Log: ${log_file}" >&2
      tail -n 160 "${log_file}" >&2 || true
      return 1
    fi
    sleep 2
  done
  echo "Timed out waiting for server on port ${port}. Log: ${log_file}" >&2
  tail -n 160 "${log_file}" >&2 || true
  return 1
}

cd "${WORK}"

EXTRA_VLLM_ARGS=()
if [[ "${USE_QWEN3_MM_FIX}" == "1" ]]; then
  EXTRA_VLLM_ARGS+=(
    --mm-encoder-attn-backend "${M3EVAL_MM_ENCODER_ATTN_BACKEND}"
    --skip-mm-profiling
  )
fi

tail -n +2 "${WORK}/run_manifest.tsv" | while IFS=$'\t' read -r model model_path; do
  [[ -n "${model}" ]] || continue
  safe="${model//\//__}"

  echo "[$(date)] START_ANSWER model=${model} temp=${ANSWER_TEMPERATURE} path=${model_path}" | tee -a "${WORK}/logs/arena_driver_answers.log"

  if [[ ! -d "${model_path}" ]]; then
    echo "Missing model path: ${model_path}" >&2
    exit 2
  fi

  answer_file="${WORK}/data/arena-hard-v2.0/model_answer/${model}.jsonl"
  answer_count=0
  if [[ -f "${answer_file}" ]]; then
    answer_count=$(wc -l < "${answer_file}")
  fi

  if [[ "${answer_count}" -ge 750 ]]; then
    echo "[$(date)] SKIP_ANSWER existing_lines=${answer_count} model=${model}" | tee -a "${WORK}/logs/arena_driver_answers.log"
    continue
  fi

  answer_log="${WORK}/logs/server_${safe}.log"
  CUDA_VISIBLE_DEVICES="${ANSWER_GPU}" python -m vllm.entrypoints.openai.api_server \
    --model "${model_path}" \
    --served-model-name "${model}" \
    --host 127.0.0.1 \
    --port "${ANSWER_PORT}" \
    --attention-backend FLASHINFER \
    --max-model-len "${ANSWER_MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${ANSWER_GPU_MEMORY_UTILIZATION}" \
    --dtype bfloat16 \
    --enforce-eager \
    --generation-config vllm \
    "${EXTRA_VLLM_ARGS[@]}" \
    > "${answer_log}" 2>&1 &
  ANSWER_SERVER_PID=$!
  echo "[$(date)] answer_server_pid=${ANSWER_SERVER_PID} gpu=${ANSWER_GPU} port=${ANSWER_PORT}" | tee -a "${WORK}/logs/arena_driver_answers.log"
  wait_for_server "${ANSWER_PORT}" "${ANSWER_SERVER_PID}" "${answer_log}"

  /usr/bin/time -v -o "${WORK}/logs/gen_answer_${safe}.time.log" \
    python gen_answer.py \
      --config-file "config/gen_answer_config_${safe}.yaml" \
      --endpoint-file "config/api_config_${safe}.yaml" \
    > "${WORK}/logs/gen_answer_${safe}.log" 2>&1

  stop_pid "${ANSWER_SERVER_PID}"
  ANSWER_SERVER_PID=""
done

echo "[$(date)] ANSWERS_DONE work=${WORK}" | tee -a "${WORK}/logs/arena_driver_answers.log"
