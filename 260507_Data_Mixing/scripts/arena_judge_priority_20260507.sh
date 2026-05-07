#!/usr/bin/env bash
set -euo pipefail

ROOT="/zhdd/home/tjshen/260415_ArcherA100"
RUN_ID="${RUN_ID:-arena_priority_$(date +%Y%m%d_%H%M%S)}"
WORK="${WORK:-${ROOT}/${RUN_ID}}"
MANIFEST="${MANIFEST:-${WORK}/run_manifest.tsv}"
ENV_NAME="${ENV_NAME:-5090_opencompass}"

JUDGE_GPU="${JUDGE_GPU:-4}"
JUDGE_PORT="${JUDGE_PORT:-9987}"
JUDGE_MODEL="${JUDGE_MODEL:-Qwen2.5-32B-Instruct}"
JUDGE_MODEL_PATH="${JUDGE_MODEL_PATH:-/zhdd/models/Qwen2.5-32B-Instruct}"
JUDGE_MAX_MODEL_LEN="${JUDGE_MAX_MODEL_LEN:-24576}"
JUDGE_MAX_TOKENS="${JUDGE_MAX_TOKENS:-4096}"
JUDGE_PARALLEL="${JUDGE_PARALLEL:-2}"
JUDGE_GPU_MEMORY_UTILIZATION="${JUDGE_GPU_MEMORY_UTILIZATION:-0.87}"
JUDGE_TEMPERATURE="${JUDGE_TEMPERATURE:-0.0}"
GPU_POLL_INTERVAL_SEC="${GPU_POLL_INTERVAL_SEC:-120}"
JUDGE_MAX_USED_MEM_MIB="${JUDGE_MAX_USED_MEM_MIB:-4096}"
LOCK_DIR="${LOCK_DIR:-${ROOT}/locks/arena_judge_gpu${JUDGE_GPU}.lock}"

mkdir -p \
  "${WORK}/logs" \
  "${WORK}/config" \
  "${WORK}/scripts" \
  "${WORK}/data/arena-hard-v2.0/model_judgment" \
  "${WORK}/cache" \
  "${ROOT}/shared_cache/tiktoken" \
  "${ROOT}/locks" \
  "${ROOT}/t"

SHORT_TMP="${ROOT}/t/aj_${RUN_ID: -10}"
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

source /home/tjshen/miniconda3/etc/profile.d/conda.sh
conda activate "${ENV_NAME}"

SERVER_PID=""
LOCK_HELD=0

stop_pid() {
  local pid="$1"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}" 2>/dev/null || true
    wait "${pid}" 2>/dev/null || true
  fi
}

cleanup() {
  stop_pid "${SERVER_PID}"
  if [[ "${LOCK_HELD}" -eq 1 ]]; then
    rmdir "${LOCK_DIR}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

acquire_lock() {
  while true; do
    if mkdir "${LOCK_DIR}" 2>/dev/null; then
      LOCK_HELD=1
      echo "[$(date)] ACQUIRED_LOCK ${LOCK_DIR}" | tee -a "${WORK}/logs/arena_driver_judge.log"
      return 0
    fi
    echo "[$(date)] WAIT_LOCK ${LOCK_DIR}" | tee -a "${WORK}/logs/arena_driver_judge.log"
    sleep "${GPU_POLL_INTERVAL_SEC}"
  done
}

wait_for_answers() {
  while true; do
    local missing=0
    while IFS=$'\t' read -r model model_path; do
      [[ "${model}" != "model" ]] || continue
      [[ -n "${model}" ]] || continue
      answer_file="${WORK}/data/arena-hard-v2.0/model_answer/${model}.jsonl"
      count=0
      if [[ -f "${answer_file}" ]]; then
        count=$(wc -l < "${answer_file}")
      fi
      if [[ "${count}" -lt 750 ]]; then
        missing=1
        echo "[$(date)] WAIT_ANSWERS model=${model} count=${count}" | tee -a "${WORK}/logs/arena_driver_judge.log"
        break
      fi
    done < "${MANIFEST}"
    if [[ "${missing}" -eq 0 ]]; then
      return 0
    fi
    sleep "${GPU_POLL_INTERVAL_SEC}"
  done
}

wait_for_gpu_memory() {
  while true; do
    used_mem=$(nvidia-smi --id="${JUDGE_GPU}" --query-gpu=memory.used --format=csv,noheader,nounits | tr -d ' ')
    if [[ "${used_mem}" -lt "${JUDGE_MAX_USED_MEM_MIB}" ]]; then
      return 0
    fi
    echo "[$(date)] WAIT_GPU_MEMORY gpu=${JUDGE_GPU} used_mem_mib=${used_mem} threshold=${JUDGE_MAX_USED_MEM_MIB}" | tee -a "${WORK}/logs/arena_driver_judge.log"
    sleep "${GPU_POLL_INTERVAL_SEC}"
  done
}

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
      tail -n 200 "${log_file}" >&2 || true
      return 1
    fi
    sleep 2
  done
  echo "Timed out waiting for server on port ${port}. Log: ${log_file}" >&2
  tail -n 200 "${log_file}" >&2 || true
  return 1
}

write_configs() {
  python - <<PY
from pathlib import Path
import yaml

work = Path("${WORK}")
manifest = Path("${MANIFEST}")
work_config = work / "config"
for line in manifest.read_text(encoding="utf-8").splitlines()[1:]:
    if not line.strip():
        continue
    model, _model_path = line.split("\t", 1)
    safe = model.replace("/", "__")
    api_path = work_config / f"api_config_{safe}.yaml"
    existing = {}
    if api_path.exists():
        loaded = yaml.safe_load(api_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            existing = loaded
    existing["${JUDGE_MODEL}"] = {
        "model": "${JUDGE_MODEL}",
        "endpoints": [{"api_base": "http://127.0.0.1:${JUDGE_PORT}/v1", "api_key": "-"}],
        "api_type": "openai",
        "parallel": int("${JUDGE_PARALLEL}"),
        "max_tokens": int("${JUDGE_MAX_TOKENS}"),
        "temperature": float("${JUDGE_TEMPERATURE}"),
    }
    arena_cfg = {
        "judge_model": "${JUDGE_MODEL}",
        "temperature": float("${JUDGE_TEMPERATURE}"),
        "max_tokens": int("${JUDGE_MAX_TOKENS}"),
        "bench_name": "arena-hard-v2.0",
        "reference": None,
        "regex_patterns": [r"\[\[([AB<>=]+)\]\]", r"\[([AB<>=]+)\]"],
        "prompt_template": "<|User Prompt|>\n{QUESTION}\n\n<|The Start of Assistant A's Answer|>\n{ANSWER_A}\n<|The End of Assistant A's Answer|>\n\n<|The Start of Assistant B's Answer|>\n{ANSWER_B}\n<|The End of Assistant B's Answer|>",
        "model_list": [model],
    }
    api_path.write_text(yaml.safe_dump(existing, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (work_config / f"arena-hard-v2.0_{safe}.yaml").write_text(
        yaml.safe_dump(arena_cfg, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
PY
}

cd "${WORK}"
wait_for_answers
write_configs
acquire_lock
wait_for_gpu_memory

judge_log="${WORK}/logs/server_${JUDGE_MODEL}_gpu${JUDGE_GPU}.log"
CUDA_VISIBLE_DEVICES="${JUDGE_GPU}" python -m vllm.entrypoints.openai.api_server \
  --model "${JUDGE_MODEL_PATH}" \
  --served-model-name "${JUDGE_MODEL}" \
  --host 127.0.0.1 \
  --port "${JUDGE_PORT}" \
  --attention-backend FLASHINFER \
  --tensor-parallel-size 1 \
  --max-model-len "${JUDGE_MAX_MODEL_LEN}" \
  --gpu-memory-utilization "${JUDGE_GPU_MEMORY_UTILIZATION}" \
  --dtype bfloat16 \
  --enforce-eager \
  --generation-config vllm \
  > "${judge_log}" 2>&1 &
SERVER_PID=$!
echo "[$(date)] judge_server_pid=${SERVER_PID} gpu=${JUDGE_GPU} port=${JUDGE_PORT}" | tee -a "${WORK}/logs/arena_driver_judge.log"
wait_for_server "${JUDGE_PORT}" "${SERVER_PID}" "${judge_log}"
sleep 10

models=()
while IFS=$'\t' read -r model model_path; do
  [[ "${model}" != "model" ]] || continue
  [[ -n "${model}" ]] || continue
  models+=("${model}")
done < "${MANIFEST}"

for model in "${models[@]}"; do
  safe="${model//\//__}"
  judgment_file="${WORK}/data/arena-hard-v2.0/model_judgment/${JUDGE_MODEL}/${model}.jsonl"
  count=0
  if [[ -f "${judgment_file}" ]]; then
    count=$(wc -l < "${judgment_file}")
  fi
  if [[ "${count}" -ge 750 ]]; then
    echo "[$(date)] SKIP_JUDGE existing_lines=${count} model=${model}" | tee -a "${WORK}/logs/arena_driver_judge.log"
    continue
  fi

  echo "[$(date)] START_JUDGE model=${model}" | tee -a "${WORK}/logs/arena_driver_judge.log"
  /usr/bin/time -v -o "${WORK}/logs/gen_judgment_${safe}.time.log" \
    python gen_judgment.py \
      --setting-file "config/arena-hard-v2.0_${safe}.yaml" \
      --endpoint-file "config/api_config_${safe}.yaml" \
    > "${WORK}/logs/gen_judgment_${safe}.log" 2>&1

  python show_result.py -j "${JUDGE_MODEL}" -c hard_prompt \
    > "${WORK}/logs/show_result_${safe}_hard_prompt.log" 2>&1 || true
  python show_result.py -j "${JUDGE_MODEL}" -c creative_writing \
    > "${WORK}/logs/show_result_${safe}_creative_writing.log" 2>&1 || true

  echo "[$(date)] DONE_JUDGE model=${model}" | tee -a "${WORK}/logs/arena_driver_judge.log"
done

python "${WORK}/scripts/arena_token_usage.py" \
  --work-dir "${WORK}" \
  --judge "${JUDGE_MODEL}" \
  --models "${models[@]}" \
  --output "${WORK}/arena_token_usage.csv" \
  > "${WORK}/logs/token_usage_final.log" 2>&1 || true

python "${WORK}/scripts/arena_tolerant_summary.py" \
  --judgment-dir "${WORK}/data/arena-hard-v2.0/model_judgment/${JUDGE_MODEL}" \
  --output "${WORK}/arena_tolerant_summary.csv" \
  --bad-label-output "${WORK}/arena_tolerant_bad_labels.csv"

echo "[$(date)] ALL_DONE work=${WORK}" | tee -a "${WORK}/logs/arena_driver_judge.log"
