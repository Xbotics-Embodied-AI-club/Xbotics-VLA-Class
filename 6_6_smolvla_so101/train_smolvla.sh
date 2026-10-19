#!/usr/bin/env bash
# 6.6 在 SO-101 上训练 SmolVLA：在自己录的 SO-101 数据上，从 lerobot/smolvla_base 出发做全参数微调。
#
# 在课程代码目录里（先 source env.sh）：
#   bash 6_6_smolvla_so101/train_smolvla.sh
# 数据默认是 4.3 节录的那份 local/put_cuboid_into_basket（两路相机 front、side）。
# 换别的数据集，在命令前面给出它的名字和两路相机：
#   REPO_ID=local/<名字> CAM_MAIN=<主视角相机> CAM_WRIST=<另一路相机> bash 6_6_smolvla_so101/train_smolvla.sh
# 命令后面还可以接任意 lerobot-train 参数，覆盖下面的同名设置，比如先跑几十步看看：
#   bash 6_6_smolvla_so101/train_smolvla.sh --steps=50 --wandb.enable=false
set -euo pipefail

REPO_ID="${REPO_ID:-local/put_cuboid_into_basket}"
CAM_MAIN="${CAM_MAIN:-front}"
CAM_WRIST="${CAM_WRIST:-side}"
OUT="$VLA_CLASS_ROOT/6_6_smolvla_so101/outputs/smolvla_$(date +%Y%m%d_%H%M%S)"

# smolvla_base 按三路相机 camera1、camera2、camera3 预训练；我们的两路接前两个，第三个空着。
RENAME="{\"observation.images.$CAM_MAIN\": \"observation.images.camera1\", \"observation.images.$CAM_WRIST\": \"observation.images.camera2\"}"

# smolvla_base 默认冻住视觉编码器、只训动作专家；换一台机器人，画面差别要视觉编码器也跟着学，
# 所以两个开关都关掉，做全参数微调。日志里可训练参数应当是 392904096（393M），不是 99880992（100M）。
# batch 16 单卡约占 16 GB 显存（batch 32 约 28 GB，batch 8 约 9 GB）。
lerobot-train \
  --policy.path=lerobot/smolvla_base \
  --policy.device=cuda \
  --policy.push_to_hub=false \
  --policy.freeze_vision_encoder=false \
  --policy.train_expert_only=false \
  --dataset.repo_id="$REPO_ID" \
  --dataset.image_transforms.enable=true \
  --rename_map="$RENAME" \
  --batch_size=16 \
  --steps=30000 \
  --policy.optimizer_lr=5e-5 \
  --policy.scheduler_warmup_steps=2000 \
  --policy.scheduler_decay_steps=30000 \
  --save_freq=5000 \
  --log_freq=100 \
  --wandb.enable=true \
  --wandb.project=smolvla-so101 \
  --output_dir="$OUT" \
  "$@"
