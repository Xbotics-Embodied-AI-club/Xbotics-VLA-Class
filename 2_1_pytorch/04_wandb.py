"""在 Lightning 训练中集成 Weights & Biases (wandb) 进行实验追踪。

基于 03_mnist_lightning.py，仅添加 WandbLogger，
自动记录训练指标、超参数和模型结构到 wandb 面板。
"""

import importlib.util
import os
from pathlib import Path

import lightning as L
from lightning.pytorch.loggers import WandbLogger

PROJECT_ROOT = Path(os.environ["VLA_CLASS_ROOT"])

# 文件名以数字开头，无法直接 import，用 importlib 加载
spec = importlib.util.spec_from_file_location(
    "mnist_lightning",
    PROJECT_ROOT / "2_1_pytorch/03_mnist_lightning.py",
)
if spec is None or spec.loader is None:
    raise ImportError("Could not load 03_mnist_lightning.py")
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)
CNNMNIST = _mod.CNNMNIST
MNISTDataModule = _mod.MNISTDataModule


def main():
    dm = MNISTDataModule(data_dir=PROJECT_ROOT / "data", batch_size=64)
    model = CNNMNIST(lr=1e-3)

    # WandbLogger 会自动记录以下内容到 wandb 面板：
    #
    # 1. 超参数 (Hyperparameters)
    #    - 来自 model.save_hyperparameters()，本例中为 lr=1e-3
    #    - Trainer 的配置参数（max_epochs, accelerator 等）
    #
    # 2. 训练指标 (Metrics) —— 来自模型中 self.log() 的调用：
    #    - train_loss: 每个 step 和每个 epoch 的训练损失
    #      (见 03_mnist_lightning.py training_step)
    #    - test_acc: 测试集准确率
    #      (见 03_mnist_lightning.py test_step)
    #
    # 3. 系统指标 (System Metrics) —— wandb 自动采集：
    #    - GPU 利用率、显存占用
    #    - CPU 利用率、内存占用
    #    - 磁盘 I/O、网络 I/O
    #
    # 4. 其他自动记录：
    #    - epoch、global_step 等训练进度信息
    #    - 运行时环境（Python 版本、OS、GPU 型号等）
    
    wandb_logger = WandbLogger(
        project="mnist-demo",  # wandb 项目名，同一项目下的 run 可对比
        name="cnn-baseline",   # 本次 run 的名称，方便在面板中区分
        log_model=False,       # 不上传模型 checkpoint 到 wandb（节省空间）
    )

    trainer = L.Trainer(
        max_epochs=3,
        accelerator="auto",
        default_root_dir=PROJECT_ROOT / "checkpoints",
        logger=wandb_logger,
    )

    trainer.fit(model, datamodule=dm)
    trainer.test(model, datamodule=dm)


if __name__ == "__main__":
    main()
