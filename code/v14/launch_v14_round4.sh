#!/bin/bash
set -euo pipefail

BASE_DIR=/zhdd/home/tjshen/260415_ArcherA100
RUN_TS=${RUN_TS:-$(date +%Y%m%d_%H%M%S)}
DIAG_DIR="${BASE_DIR}/diag_5090_Hao_v14_round4_${RUN_TS}"

mkdir -p "${DIAG_DIR}"
cd "${BASE_DIR}/v14"

nohup env \
    CONDA_ENV_NAME=llama2_vllm \
    CUDA_HOME=/usr/local/cuda-12.9 \
    PATH="/usr/local/cuda-12.9/bin:${PATH}" \
    CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-1,2,4,5} \
    WORK_DIR="${BASE_DIR}/v14" \
    RUNTIME_DIR="${BASE_DIR}/rt_v14" \
    RAY_TMPDIR="/tmp/rv14r4" \
    RAY_PORT=${RAY_PORT:-6790} \
    MODEL_PATH=/zhdd/home/tjshen/260415_ArcherA100/v14/output_5090_Hao/ArcherCodeR-V14-Qwen25-1_5B-5090Hao/train_v14_5090hao_qwen25_1_5b_4gpu_bsz32_20260512_190827/global_step_50_merged \
    REWARD_MODEL_PATH=/zhdd/home/tjshen/260413_Backup_model_resume_20260323_031320/Skywork-Reward-Llama-3.1-8B-v0.2 \
    TRAIN_FILE="${BASE_DIR}/v13/data/train/Mix_AirRep_nonrepeated_sysprom.json" \
    TEST_FILE="${BASE_DIR}/v13/data/test/livecodebench_v5.json" \
    TARGET_MATH_FILE="${BASE_DIR}/v13/data/test/AIME2025.json" \
    TARGET_CODE_FILE="${BASE_DIR}/v13/data/test/LCB.json" \
    TARGET_GENERAL_FILE="${BASE_DIR}/v13/data/test/Arena_question.json" \
    PROJECT_NAME=ArcherCodeR-V14-Qwen25-1_5B-5090Hao \
    EXP_NAME="train_v14_round4_${RUN_TS}" \
    OUTPUT_ROOT="${BASE_DIR}/v14/output_5090_Hao" \
    DYNAMIC_METHOD=sample_taylor_v13 \
    TOTAL_TRAINING_STEPS=50 \
    SAVE_FREQ=50 \
    SAVE_STEPS=10,50 \
    TRAIN_PROMPT_BSZ=32 \
    TRAIN_PROMPT_MINI_BSZ=8 \
    ROLLOUT_GPU_MEMORY_UTILIZATION=0.45 \
    SHADOW_ANCHOR_SIZE_PER_DOMAIN=128 \
    CANDIDATE_MULTIPLIER=4 \
    GRAD_PROJECTION_DIM=256 \
    CURVATURE_REFRESH_FREQ=50 \
    FULL_DATASET_EMBEDDING_BATCH_SIZE=4 \
    FULL_TRAIN_MAX_SAMPLES_PER_CATEGORY=4 \
    FULL_TARGET_MAX_SAMPLES_PER_CATEGORY=4 \
    DOMAIN_SOFTMAX_TEMPERATURE=0.3 \
    DOMAIN_MIN_WEIGHT=0.05 \
    DOMAIN_BUDGET_SMOOTH=0.5 \
    DISABLE_PYTORCH_CUDA_ALLOC_CONF=1 \
    RAY_memory_usage_threshold=0.99 \
    ./dynamic_train_v14_5090_hao.sh \
    > "${DIAG_DIR}/launch.log" 2>&1 &

echo "PID=$!"
echo "DIAG_DIR=${DIAG_DIR}"
echo "LOG=${DIAG_DIR}/launch.log"
echo "TRAIN_DIR=${BASE_DIR}/v14/output_5090_Hao/ArcherCodeR-V14-Qwen25-1_5B-5090Hao/train_v14_round4_${RUN_TS}"
echo ""
echo "=== V14 Round 4 Config Changes ==="
echo "  DOMAIN_SOFTMAX_TEMPERATURE: 1.0 -> 0.3 (amplify score differences)"
echo "  DOMAIN_MIN_WEIGHT: 0.15 -> 0.05 (wider dynamic range)"
echo "  DOMAIN_BUDGET_SMOOTH: 0.2 -> 0.5 (faster response)"
echo "  Second floor in _v13_budget_weights: REMOVED"
echo "  Resume from: Round2 step50 merged"
