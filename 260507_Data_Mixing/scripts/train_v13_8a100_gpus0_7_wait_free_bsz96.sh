#!/usr/bin/env bash
set -euo pipefail

# V13 Qwen2.5-1.5B two-GPU watcher launcher.
# Intended host: 8A100.
# Intended physical GPUs: 0,7.
# This script waits until both cards have enough free memory, then launches one
# background training job. It does not kill other users' processes.

BASE=/zhdd/home/tjshen/260415_ArcherA100
WORK_DIR=$BASE/v13
SCRIPT=$WORK_DIR/dynamic_train_v13_a100_smoke_bsz4_20step.sh
PROJECT_NAME=ArcherCodeR-V13-Qwen25-1_5B-8A100
OUTPUT_ROOT=$BASE/v13/output_8A100_2gpu

MIN_FREE_MB=${MIN_FREE_MB:-70000}
CHECK_INTERVAL=${CHECK_INTERVAL:-60}
RAY_PORT=${RAY_PORT:-6787}
RUNTIME_DIR=${RUNTIME_DIR:-$BASE/t807d}
RAY_TMPDIR=${RAY_TMPDIR:-$BASE/r807d}

mkdir -p "$RUNTIME_DIR" "$RAY_TMPDIR" "$OUTPUT_ROOT"

echo "[$(date)] watcher started on $(hostname), waiting for GPU0 and GPU7 free >= ${MIN_FREE_MB} MiB"
echo "WORK_DIR=$WORK_DIR"
echo "SCRIPT=$SCRIPT"

while true; do
  mapfile -t free_vals < <(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0,7)
  free0=$(echo "${free_vals[0]:-0}" | tr -dc '0-9')
  free7=$(echo "${free_vals[1]:-0}" | tr -dc '0-9')
  used_line=$(nvidia-smi --query-gpu=index,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits -i 0,7 | paste -sd '; ' -)
  echo "[$(date)] gpu_state=${used_line}"

  if [ "${free0:-0}" -ge "$MIN_FREE_MB" ] && [ "${free7:-0}" -ge "$MIN_FREE_MB" ]; then
    RUN_TS=$(date +%Y%m%d_%H%M%S)
    EXP_NAME=train_8a100_v13_qwen25_1_5b_2gpu_gpus0_7_bsz96_mini48_util070_noexpand_save100_${RUN_TS}
    OUT_DIR=$OUTPUT_ROOT/$PROJECT_NAME/$EXP_NAME
    mkdir -p "$OUT_DIR"
    TRAIN_LOG=$OUT_DIR/train.log

    cat > "$OUT_DIR/run_env.txt" <<EOF
RUN_TS=$RUN_TS
HOST=$(hostname)
CUDA_VISIBLE_DEVICES=0,7
TRAIN_PROMPT_BSZ=96
TRAIN_PROMPT_MINI_BSZ=48
ROLLOUT_GPU_MEMORY_UTILIZATION=0.70
DISABLE_PYTORCH_CUDA_ALLOC_CONF=1
SAVE_FREQ=100
TOTAL_TRAINING_STEPS=2000
RAY_PORT=$RAY_PORT
RUNTIME_DIR=$RUNTIME_DIR
RAY_TMPDIR=$RAY_TMPDIR
OUTPUT_ROOT=$OUTPUT_ROOT
PROJECT_NAME=$PROJECT_NAME
EXP_NAME=$EXP_NAME
WORK_DIR=$WORK_DIR
SCRIPT=$SCRIPT
EOF

    echo "[$(date)] launching EXP_NAME=$EXP_NAME"
    echo "OUT_DIR=$OUT_DIR"

    (
      cd "$WORK_DIR"
      CUDA_VISIBLE_DEVICES=0,7 \
      CONDA_ENV_NAME=llama2_vllm_copy \
      WORK_DIR="$WORK_DIR" \
      RUNTIME_DIR="$RUNTIME_DIR" \
      RAY_TMPDIR="$RAY_TMPDIR" \
      RAY_PORT=$RAY_PORT \
      RAY_RUNTIME_ENV_AGENT_PORT=30101 \
      RAY_DASHBOARD_AGENT_LISTEN_PORT=30102 \
      RAY_DASHBOARD_AGENT_GRPC_PORT=30103 \
      RAY_METRICS_EXPORT_PORT=30105 \
      RAY_OBJECT_MANAGER_PORT=30106 \
      RAY_NODE_MANAGER_PORT=30107 \
      RAY_MIN_WORKER_PORT=31100 \
      RAY_MAX_WORKER_PORT=39999 \
      DISABLE_PYTORCH_CUDA_ALLOC_CONF=1 \
      PROJECT_NAME="$PROJECT_NAME" \
      EXP_NAME="$EXP_NAME" \
      OUTPUT_ROOT="$OUTPUT_ROOT" \
      MODEL_PATH=/zhdd/models/Qwen2.5-1.5B-Instruct \
      REWARD_MODEL_PATH=/zhdd/home/tjshen/260413_Backup_model_resume_20260323_031320/Skywork-Reward-Llama-3.1-8B-v0.2 \
      TRAIN_FILE=$BASE/v13/data/train/Mix_AirRep_nonrepeated_sysprom.json \
      TEST_FILE=$BASE/v13/data/test/livecodebench_v5.json \
      TARGET_MATH_FILE=$BASE/v13/data/test/AIME2025.json \
      TARGET_CODE_FILE=$BASE/v13/data/test/LCB.json \
      TARGET_GENERAL_FILE=$BASE/v13/data/test/Arena_question.json \
      TRAIN_PROMPT_BSZ=96 \
      TRAIN_PROMPT_MINI_BSZ=48 \
      ROLLOUT_GPU_MEMORY_UTILIZATION=0.70 \
      FULL_DATASET_EMBEDDING_BATCH_SIZE=4 \
      SHADOW_ANCHOR_SIZE_PER_DOMAIN=128 \
      CANDIDATE_MULTIPLIER=4 \
      GRAD_PROJECTION_DIM=256 \
      CURVATURE_REFRESH_FREQ=50 \
      TOTAL_TRAINING_STEPS=2000 \
      SAVE_FREQ=100 \
      FULL_TRAIN_MAX_SAMPLES_PER_CATEGORY=4 \
      FULL_TARGET_MAX_SAMPLES_PER_CATEGORY=4 \
      bash "$SCRIPT"
    ) > "$TRAIN_LOG" 2>&1 &

    echo $! > "$OUT_DIR/driver.pid"
    echo "[$(date)] training background pid=$(cat "$OUT_DIR/driver.pid")"
    exit 0
  fi

  sleep "$CHECK_INTERVAL"
done
