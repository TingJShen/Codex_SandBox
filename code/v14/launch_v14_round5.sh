#!/bin/bash
set -euo pipefail

BASE_DIR=/zhdd/home/tjshen/260415_ArcherA100
RUN_TS=${RUN_TS:-$(date +%Y%m%d_%H%M%S)}
DIAG_DIR="${BASE_DIR}/diag_5090_Hao_v14_round5_${RUN_TS}"

mkdir -p "${DIAG_DIR}"
cd "${BASE_DIR}/v14"

nohup env \
    CONDA_ENV_NAME=llama2_vllm \
    CUDA_HOME=/usr/local/cuda-12.9 \
    PATH="/usr/local/cuda-12.9/bin:${PATH}" \
    CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0,1,2,3} \
    WORK_DIR="${BASE_DIR}/v14" \
    RUNTIME_DIR="${BASE_DIR}/rt_v14" \
    RAY_TMPDIR="/tmp/rv14r5" \
    RAY_PORT=${RAY_PORT:-6791} \
    MODEL_PATH=/zhdd/home/tjshen/260415_ArcherA100/v14/output_5090_Hao/ArcherCodeR-V14-Qwen25-1_5B-5090Hao/train_v14_round4c_20260513_085824/global_step_50_merged \
    REWARD_MODEL_PATH=/zhdd/home/tjshen/260413_Backup_model_resume_20260323_031320/Skywork-Reward-Llama-3.1-8B-v0.2 \
    TRAIN_FILE="${BASE_DIR}/v13/data/train/Mix_AirRep_nonrepeated_sysprom.json" \
    TEST_FILE="${BASE_DIR}/v13/data/test/livecodebench_v5.json" \
    TARGET_MATH_FILE="${BASE_DIR}/v13/data/test/AIME2025.json" \
    TARGET_CODE_FILE="${BASE_DIR}/v13/data/test/LCB.json" \
    TARGET_GENERAL_FILE="${BASE_DIR}/v13/data/test/Arena_question.json" \
    PROJECT_NAME=ArcherCodeR-V14-Qwen25-1_5B-5090Hao \
    EXP_NAME="train_v14_round5_${RUN_TS}" \
    OUTPUT_ROOT="${BASE_DIR}/v14/output_5090_Hao" \
    DYNAMIC_METHOD=sample_taylor_v13 \
    TOTAL_TRAINING_STEPS=50 \
    SAVE_FREQ=50 \
    SAVE_STEPS=10,50 \
    TRAIN_PROMPT_BSZ=8 \
    TRAIN_PROMPT_MINI_BSZ=4 \
    N_RESP_PER_PROMPT=8 \
    KL_LOSS_COEF=0.0 \
    CLIP_RATIO_HIGH=0.28 \
    ROLLOUT_GPU_MEMORY_UTILIZATION=0.15 \
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
    OFFLOAD=True \
    RAY_memory_usage_threshold=0.99 \
    ./dynamic_train_v14_5090_hao.sh \
    > "${DIAG_DIR}/launch.log" 2>&1 &

echo "PID=$!"
echo "DIAG_DIR=${DIAG_DIR}"
echo "LOG=${DIAG_DIR}/launch.log"
echo "TRAIN_DIR=${BASE_DIR}/v14/output_5090_Hao/ArcherCodeR-V14-Qwen25-1_5B-5090Hao/train_v14_round5_${RUN_TS}"
echo ""
echo "=== V14 Round 5 Engineering Optimizations ==="
echo "  [KEY] N_RESP_PER_PROMPT: 2 -> 8 (4x more stable advantage estimation)"
echo "  [KEY] KL_LOSS_COEF: 0.001 -> 0.0 (remove KL penalty, per DAPO findings)"
echo "  [KEY] CLIP_RATIO_HIGH: 0.2 -> 0.28 (allow larger policy updates)"
echo "  TRAIN_PROMPT_BSZ: 32 -> 8 (compensate for 4x more responses)"
echo "  TRAIN_PROMPT_MINI_BSZ: 8 -> 4"
echo "  Resume from: Round4c step50 merged"
echo ""
echo "  Rationale: With group_size=2, GRPO advantage has extreme variance."
echo "  Literature shows group_size>=8 is critical for stable learning."
echo "  Removing KL allows the model to explore further from reference."
