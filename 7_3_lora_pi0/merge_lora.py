"""把训好的 LoRA 适配器合并回 Pi0，存成一份完整的权重。

训练存下来的只有适配器（几百 MB），用的时候要先装基座、再挂适配器。部署用的推理服务
（8.1 节那套）按完整权重来读，所以部署前先合并：每个挂了 LoRA 的矩阵 W 换成 W + (α/r)·BA，
旁路就没有了，得到的是一个普通的 Pi0，和全参数微调出来的权重用法一样。

用法（在课程代码目录里，先 source env.sh）：
  python 7_3_lora_pi0/merge_lora.py <训练保存的 pretrained_model 目录> <输出目录>
例：
  python 7_3_lora_pi0/merge_lora.py 7_3_lora_pi0/outputs/lora_pi0_xxx/checkpoints/last/pretrained_model 7_3_lora_pi0/outputs/merged
训练过不止一次时，outputs 下有好几个 lora_pi0_<时间>，第一个参数写明具体是哪一个，不要用通配符。
"""
import shutil
import sys
from pathlib import Path

from peft import PeftConfig, PeftModel

from lerobot.configs.policies import PreTrainedConfig
from lerobot.policies.factory import get_policy_class


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("用法: python 7_3_lora_pi0/merge_lora.py <训练保存的 pretrained_model 目录> <输出目录>\n"
                 f"收到 {len(sys.argv) - 1} 个参数；路径里的通配符匹配到了几个训练目录时也会这样，请写明具体是哪一个")
    adapter_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    if not (adapter_dir / "adapter_config.json").is_file():
        sys.exit(f"{adapter_dir} 里没有 adapter_config.json：第一个参数要指向训练保存的 pretrained_model 目录")
    if (out_dir / "adapter_config.json").exists():
        sys.exit(f"{out_dir} 是一份训练保存的适配器目录，不能当输出目录，换一个新目录")

    # 训练保存的 config.json 是训练时的策略配置（相机、关节数都按我们的数据）；
    # adapter_config.json 记着它的基座是哪一个
    cfg = PreTrainedConfig.from_pretrained(adapter_dir)
    base = PeftConfig.from_pretrained(adapter_dir).base_model_name_or_path
    print(f"[合并] 基座: {base}")
    print(f"[合并] 适配器: {adapter_dir}")

    policy = get_policy_class(cfg.type).from_pretrained(base, config=cfg)
    policy = PeftModel.from_pretrained(policy, adapter_dir)
    policy = policy.merge_and_unload()

    # 合并之后它就是一份普通的权重了
    policy.config.use_peft = False
    policy.save_pretrained(out_dir)

    # 前后处理（相机改名、数据归一化、指令分词）和训练时一样，原样拷过去
    for f in adapter_dir.iterdir():
        if f.name.startswith(("policy_preprocessor", "policy_postprocessor")):
            shutil.copy2(f, out_dir / f.name)
    shutil.copytree(adapter_dir / "tokenizer", out_dir / "tokenizer", dirs_exist_ok=True)
    print(f"[合并] 完成，完整权重在: {out_dir}")


if __name__ == "__main__":
    main()
