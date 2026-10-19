#!/usr/bin/env bash
# 7.3 用 LoRA 微调 Pi0：在自己录的 SO-101 数据上训练。
#
# 在课程代码目录里（先 source env.sh）：
#   bash 7_3_lora_pi0/train_lora_pi0.sh
# 数据默认是 4.3 节录的那份 local/put_cuboid_into_basket（两路相机 front、side）。
# 换别的数据集，在命令前面给出它的名字和两路相机：
#   REPO_ID=local/<名字> CAM_MAIN=<主视角相机> CAM_WRIST=<另一路相机> bash 7_3_lora_pi0/train_lora_pi0.sh
# 命令后面还可以接任意 lerobot-train 参数，覆盖下面的同名设置，比如先跑几十步看看：
#   bash 7_3_lora_pi0/train_lora_pi0.sh --steps=50 --wandb.enable=false
set -euo pipefail

REPO_ID="${REPO_ID:-local/put_cuboid_into_basket}"
CAM_MAIN="${CAM_MAIN:-front}"
CAM_WRIST="${CAM_WRIST:-side}"
OUT="$VLA_CLASS_ROOT/7_3_lora_pi0/outputs/lora_pi0_$(date +%Y%m%d_%H%M%S)"

# LoRA 挂在三组注意力的 q、v 投影上：视觉编码器 27 层、语言模型 18 层、动作专家 18 层，一共 126 个矩阵。
# 只挂动作专家（库里的默认做法）换到一台新机器人上学不动，视觉和语言两组也要一起挂。
TARGETS='(model\.paligemma_with_expert\.(gemma_expert|paligemma\.model\.language_model|paligemma\.model\.vision_tower\.vision_model\.encoder)\..*\.(q|v)_proj)'
# 这五层把机器人的关节状态和动作接进模型，本身不大，整层训练，不做低秩近似。
FULL='["state_proj","action_in_proj","action_out_proj","action_time_mlp_in","action_time_mlp_out"]'
# Pi0 有三个相机入口：主视角和左右两个手腕。我们的两路相机接前两个，第三个空着。
RENAME="{\"observation.images.$CAM_MAIN\": \"observation.images.base_0_rgb\", \"observation.images.$CAM_WRIST\": \"observation.images.left_wrist_0_rgb\"}"

lerobot-train \
  --policy.path=lerobot/pi0_base \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --policy.gradient_checkpointing=true \
  --peft.method_type=LORA \
  --peft.r=256 \
  --peft.target_modules="$TARGETS" \
  --peft.full_training_modules="$FULL" \
  --dataset.repo_id="$REPO_ID" \
  --rename_map="$RENAME" \
  --batch_size=16 \
  --steps=30000 \
  --policy.optimizer_lr=3e-4 \
  --policy.scheduler_warmup_steps=2000 \
  --policy.scheduler_decay_steps=30000 \
  --save_freq=5000 \
  --log_freq=100 \
  --wandb.enable=true \
  --wandb.project=lora-pi0 \
  --output_dir="$OUT" \
  "$@"
