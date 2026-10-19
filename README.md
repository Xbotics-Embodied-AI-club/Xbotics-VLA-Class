# Xbotics VLA 课程代码

VLA 课程各章的配套代码。目录名前面的编号就是讲义的章节号，按编号顺序读、按编号顺序跑。

| 目录 | 章节 | 内容 |
| --- | --- | --- |
| `2_1_pytorch/` | 2.1 PyTorch 及 PyTorch Lightning | MNIST 手写数字：纯 PyTorch、Lightning、接 wandb |
| `2_3_GPT2/` | 2.3 GPT2 的实现 | 从零写一个 GPT2，在中文语料上训练 |
| `3_1_robotics/` | 3.1 机器人核心数学基础 | Panda、SO-101 的机器人模型文件 |
| `3_4_libero/` | 3.4 LIBERO 仿真环境 | 在 LIBERO 里建场景、看相机、动机械臂 |
| `3_5_SO101/` | 3.5 SO101 实物 | 常用命令、串口固定设备名 |
| `4_2_lerobot_dataset/` | 4.2 LeRobot 数据集格式 | 读一份 LeRobot 数据集、可视化 |
| `4_3_tele_so101/` | 4.3 SO101 数采 | 主从臂遥操作、录数据 |
| `5_2_ACT/` | 5.2 ACT 算法 | 在 LIBERO 上训练 ACT，本地推理与远程推理 |
| `6_3_pi0/` | 6.2 / 6.3 Pi0 | 用微调好的 Pi0 在 LIBERO 里完成任务 |
| `6_6_smolvla_so101/` | 6.6 在 SO101 上训练 SmolVLA | 在自己录的 SO-101 数据上全参数微调 SmolVLA |
| `7_3_lora_pi0/` | 7.3 利用 LoRA 微调 Pi0 | 在自己录的 SO-101 数据上给 Pi0 挂 LoRA 训练，训好后合并成完整权重 |
| `lerobot/` | —— | Xbotics 维护版 LeRobot 0.6.1 的源码，`uv sync` 时从这里装（`lerobot[all]`）；x86 上 SO-101 仿真器随它一起装上 |

## 需要什么

- 一台 x86 的 Linux 电脑（Ubuntu 22.04 / 24.04），带 NVIDIA 显卡，驱动 570 以上：各章的训练、推理、仿真都在它上面跑
- 接 SO-101 真机时的端侧控制设备，比如你自己没有显卡的电脑：只用来控制真机，接主从臂遥操作、录数据、执行推理服务器发来的动作，不跑模型；它装的也是同一套环境
- 能访问 GitHub 和 Hugging Face：课程代码从 GitHub 克隆，数据集和模型从 Hugging Face 下载
- 6.3 的 Pi0 要用到 Google 的 PaliGemma：先在 <https://huggingface.co/google/paligemma-3b-pt-224> 页面点同意条款，
  再 `export HF_TOKEN=<你的 token>`

## 安装

```bash
sudo apt install -y build-essential cmake git   # egl-probe 要现场编译；git 用来克隆课程代码，SO-101 仿真器也从 GitHub 装
curl -LsSf https://astral.sh/uv/install.sh | sh # 装 uv（已经有就跳过）

git clone https://github.com/Xbotics-Embodied-AI-club/Xbotics-VLA-Class.git
cd Xbotics-VLA-Class
uv sync --extra x86        # 按 uv.lock 装好整门课的环境，装在 .venv/ 里；有显卡的电脑和端侧控制设备都是这一句
source env.sh              # 设好各章要用的环境变量，激活 .venv
python download_assets.py  # 准备 LIBERO 场景资产和 GPT2 语料（端侧控制设备上不用跑）
```

以后每开一个新终端，进到这个目录先 `source env.sh`。课程代码有更新时，进到这个目录 `git pull`，再 `uv sync --extra x86`。

环境只有一份：所有机器装的包都一样（`lerobot[all]` 加各章用到的包，用不上的也装上）。`--extra x86` 让 PyTorch 从它官方的
CUDA 12.8 源装；端侧控制设备没有显卡，这些 CUDA 的库装上了用不到。只敲 `uv sync` 不带这个参数，PyTorch 不会从这个源装，
装出来的不是课程测过的环境。

端侧控制设备上做的是控制真机：接臂、遥操作、录数据（3.5、4.3）和远程推理的客户端；训练、推理服务器和 LIBERO 仿真都在
有显卡的电脑上跑，所以端侧控制设备上不用跑 `download_assets.py`。

## 从 0523 版更新

新版用 git 克隆到一个**新目录**，照上面「安装」从头装一遍，不要放进旧目录里覆盖：LeRobot 从 0.5.0 升到了 0.6.1，
旧的 `.venv` 不能接着用。旧目录里你自己训练出来的东西（比如 `5_2_ACT/outputs/`）直接拷到新目录同样的位置。

两版的差别：

- **LeRobot 0.5.0 → Xbotics 维护版 0.6.1**，PyTorch 等依赖的版本由它来定；SO-101 仿真器随它一起装上，
  sim2real 那一集里的命令（`lerobot-eval --env.type=so101_sim`、`--robot.type=so101_sim` 等）都能直接用。
- **装环境要带 `--extra x86`**，见「安装」。课程里的 `lerobot/` 和维护版的标签是同一份源码，只去掉了它 pyproject 里的
  torch 源设置（PyTorch 从哪个源装统一由课程的 pyproject 决定），以及 `.gitattributes` 里的 Git LFS 设置（那几行让装了 git-lfs 的电脑在 `git clone` 时去下载测试用的文件，这个仓库里没有它们，克隆会失败）。
- **各章代码的写法不变**。为了跟 0.6.1 对上，改了这几处，调用方式都没动：
  - 0.6.1 删掉了 `add_envs_task`：在 `6_3_pi0/pi0_demo.py` 和 `5_2_ACT` 的两个推理笔记本里照原样补了一个；
  - 0.6.1 的 LIBERO 把「是否成功」从 `info["final_info"]` 挪到了 `info` 里：这三个文件两处都认；
  - `5_2_ACT/train_act_libero.py`：`eval_freq` 改名为 `env_eval_freq`，`pull_from_repo` 改名为 `_pull_from_repo`；
  - `hw_to_dataset_features` 挪到了 `lerobot.utils.feature_utils`。
- **修了一个原来就有的问题**：`5_2_ACT/train_act_libero.py` 原来按轨迹条数算一个 epoch 有几步，
  算出来只有 1 步，每 2 步就评测并存一次检查点，几十分钟就能写满十几 GB。现在按帧数算，
  检查点改成每 1 万步存一次（训练结束时也会存），一个检查点约 600 MB。
- **新增**：`6_6_smolvla_so101/`、`7_3_lora_pi0/`（6.6、7.3 节的实操代码）、`env.sh`（环境变量）、`download_assets.py`（资产）、`uv.lock`（锁定的依赖版本）、这份 README。
  LIBERO 的配置改放在课程目录的 `.libero/` 里，不再用 `~/.libero`：那里如果留着以前别的环境写的配置，
  LIBERO 会去那个环境里找场景文件。

## 各章怎么跑

先 `source env.sh`。笔记本（`.ipynb`）用 VS Code 或 Jupyter 打开，内核选 `.venv` 里的 Python，从上往下逐格运行。

| 章节 | 怎么跑 | 说明 |
| --- | --- | --- |
| 2.1 | `python 2_1_pytorch/02_mnist.py`<br>`python 2_1_pytorch/03_mnist_lightning.py`<br>`python 2_1_pytorch/04_wandb.py` | 第一次会自动下载 MNIST。04 要先 `wandb login`，不想上传就 `export WANDB_MODE=offline` |
| 2.3 | `2_3_GPT2/GPT2.ipynb` | 语料由 `download_assets.py` 准备；完整训练 10 轮要很久，看到 loss 在降就可以停 |
| 3.4 | `3_4_libero/libero_demo.ipynb` | |
| 4.2 | `4_2_lerobot_dataset/dataset_demo.ipynb`<br>`bash 4_2_lerobot_dataset/viz_method2.sh` | 第一次会自动下载 `lerobot/libero` 数据集 |
| 4.3 | `bash 4_3_tele_so101/tele.sh`<br>`bash 4_3_tele_so101/record.sh` | 要接 SO-101 主从臂和两路相机；串口先按 `3_5_SO101/udev_serial_port_binding.md` 固定成 `/dev/ttyFollower`、`/dev/ttyLeader` |
| 5.2 训练 | `python 5_2_ACT/train_act_libero.py` | 输出在 `5_2_ACT/outputs/act_libero_goal_plate_<时间>/` |
| 5.2 推理 | `5_2_ACT/infer_act_libero.ipynb` | 把笔记本里的 `POLICY_PATH` 改成你训练出来的 `checkpoints/<步数>/pretrained_model` |
| 5.2 远程推理 | `python 5_2_ACT/infer_act_libero_server.py`，再开一个终端跑 `5_2_ACT/infer_act_libero_client.ipynb` | `POLICY_PATH` 同上 |
| 6.3 | `python 6_3_pi0/pi0_demo.py` | 第一次会自动下载 Pi0 权重；成功后录像写到 `6_3_pi0/output/pi0_libero_success.mp4` |
| 6.6 | `bash 6_6_smolvla_so101/train_smolvla.sh` | 默认用 4.3 录的 `local/put_cuboid_into_basket`；换数据集在命令前给 `REPO_ID=… CAM_MAIN=… CAM_WRIST=…`。全参数微调，日志里可训练参数应是 392904096（393M）。单卡 batch 16 约占 16 GB 显存。输出在 `6_6_smolvla_so101/outputs/smolvla_<时间>/`，部署见 8.1 |
| 7.3 训练 | `bash 7_3_lora_pi0/train_lora_pi0.sh` | 默认用 4.3 录的 `local/put_cuboid_into_basket`；换数据集在命令前给 `REPO_ID=… CAM_MAIN=… CAM_WRIST=…`。第一次会下载 Pi0 基座（14 GB），要先同意 PaliGemma 的条款（见「需要什么」）。单卡 batch 16 约占 24 GB 显存；卡只有 24 GB 时在命令后加 `--batch_size=8`（约 20 GB）。输出在 `7_3_lora_pi0/outputs/lora_pi0_<时间>/` |
| 7.3 合并 | `python 7_3_lora_pi0/merge_lora.py <训练保存的模型目录>/pretrained_model <输出目录>` | 训练保存的只有 LoRA 适配器；第一个参数写明是哪一次训练（不要用通配符）；合并回 Pi0 得到完整权重，部署时和全参数微调的权重一样用 |
