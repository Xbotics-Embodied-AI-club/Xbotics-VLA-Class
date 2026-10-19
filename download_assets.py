"""准备两样 LeRobot 不会自动下载的资产（先 source env.sh）：

    python download_assets.py

- LIBERO 场景资产：按当前环境写好 LIBERO 的配置（不写的话它第一次 import 会停下来问资产放哪），
  把资产下到 $VLA_CLASS_ASSETS_ROOT/libero/assets，并把 libero_goal 第 5 个任务的场景预先建一遍（3.4、5.2、6.3）
- GPT2 那节用的中文语料：下载后解压成 $VLA_CLASS_ASSETS_ROOT/2_3_GPT2/mobvoi_seq_monkey_general_open_corpus.jsonl（2.3）

各章用到的数据集与模型（lerobot/libero、Pi0 权重等）在第一次用到时由 LeRobot 自己从 Hugging Face 下载，不用在这里预先下。
"""

from __future__ import annotations

import os
import shutil
import site
import zipfile
from pathlib import Path

from huggingface_hub import hf_hub_download

MONKEY_DATASET_ID = "arron666/seq_monkey"
MONKEY_FILENAME = "mobvoi_seq_monkey_general_open_corpus.zip"
LIBERO_SUITE = "libero_goal"
LIBERO_TASK_ID = 5

ASSETS_ROOT = Path(os.environ["VLA_CLASS_ASSETS_ROOT"])
MONKEY_OUTPUT = ASSETS_ROOT / "2_3_GPT2/mobvoi_seq_monkey_general_open_corpus.jsonl"
LIBERO_ASSETS = ASSETS_ROOT / "libero/assets"


def libero_benchmark_root() -> Path:
    for site_dir in site.getsitepackages():
        candidate = Path(site_dir) / "libero/libero"
        if (candidate / "bddl_files").exists() and (candidate / "init_files").exists():
            return candidate
    raise FileNotFoundError("没找到装好的 LIBERO（libero/libero 下的 bddl_files 与 init_files），先 uv sync")


def write_libero_config() -> None:
    config_dir = Path(os.environ.get("LIBERO_CONFIG_PATH", Path.home() / ".libero")).expanduser()
    config_file = config_dir / "config.yaml"
    benchmark_root = libero_benchmark_root()
    paths = {
        "assets": LIBERO_ASSETS,
        "bddl_files": benchmark_root / "bddl_files",
        "benchmark_root": benchmark_root,
        "datasets": ASSETS_ROOT / "libero/datasets",
        "init_states": benchmark_root / "init_files",
    }
    for key in ("assets", "datasets"):
        paths[key].mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text("".join(f"{k}: {v}\n" for k, v in paths.items()), encoding="utf-8")


def prepare_libero() -> None:
    write_libero_config()
    from libero.libero.utils.download_utils import download_assets_from_huggingface

    download_assets_from_huggingface(download_dir=str(LIBERO_ASSETS))

    # 把要用的那个场景建一遍：第一次建场景会再补拉缺的资产，放在这里做，上课时就不用等
    import libero.libero as libero_benchmark
    from lerobot.envs.configs import LiberoEnv as LiberoEnvConfig
    from lerobot.envs.factory import make_env

    libero_benchmark._assets_path_cache = str(LIBERO_ASSETS)
    env_cfg = LiberoEnvConfig(task=LIBERO_SUITE, task_ids=[LIBERO_TASK_ID], obs_type="pixels_agent_pos",
                              observation_height=256, observation_width=256, episode_length=2)
    envs = make_env(env_cfg, n_envs=1)
    for env in envs[LIBERO_SUITE].values():
        env.reset(seed=[7])
        env.close()


def prepare_monkey_corpus() -> None:
    if MONKEY_OUTPUT.exists() and MONKEY_OUTPUT.stat().st_size > 0:
        print(f"[语料] 已经在 {MONKEY_OUTPUT}")
        return
    zip_path = hf_hub_download(repo_id=MONKEY_DATASET_ID, repo_type="dataset", filename=MONKEY_FILENAME)
    MONKEY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = MONKEY_OUTPUT.with_suffix(".jsonl.tmp")
    with zipfile.ZipFile(zip_path) as archive:
        name = next(n for n in archive.namelist() if n.endswith("mobvoi_seq_monkey_general_open_corpus.jsonl"))
        with archive.open(name) as src, tmp.open("wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
    tmp.replace(MONKEY_OUTPUT)


def main() -> None:
    os.environ.setdefault("MUJOCO_GL", "egl")
    print(f"[LIBERO] 资产放在 {LIBERO_ASSETS}")
    prepare_libero()
    print(f"[语料] {MONKEY_DATASET_ID} → {MONKEY_OUTPUT}")
    prepare_monkey_corpus()
    print("准备好了")


if __name__ == "__main__":
    main()
