# 课程代码的环境变量。每次开新终端，在课程代码目录里执行一次：
#   source env.sh
# 各章脚本用 VLA_CLASS_ROOT 找代码目录、用 VLA_CLASS_ASSETS_ROOT 找下载下来的资产
# （LIBERO 场景资产、GPT2 语料）。资产想放到别的盘，先 export VLA_CLASS_ASSETS_ROOT 再 source。
export VLA_CLASS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VLA_CLASS_ASSETS_ROOT="${VLA_CLASS_ASSETS_ROOT:-$VLA_CLASS_ROOT/assets}"
# LIBERO 的配置放在课程目录里（默认的 ~/.libero 可能是以前装的别的环境留下的，指着那边的文件）
export LIBERO_CONFIG_PATH="${LIBERO_CONFIG_PATH:-$VLA_CLASS_ROOT/.libero}"
# LIBERO 与 MuJoCo 在没有显示器的机器上用 EGL 离屏渲染
export MUJOCO_GL="${MUJOCO_GL:-egl}"
if [ -f "$VLA_CLASS_ROOT/.venv/bin/activate" ]; then
    source "$VLA_CLASS_ROOT/.venv/bin/activate"
fi
echo "VLA_CLASS_ROOT=$VLA_CLASS_ROOT"
echo "VLA_CLASS_ASSETS_ROOT=$VLA_CLASS_ASSETS_ROOT"
