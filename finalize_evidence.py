"""C4D 证据一键补全脚本（在本机正常网络环境运行）。

作用：把本提交因沙箱网络受限而未能采集的「实际运行证据」一次性补齐，
产出挑战《需要提交什么》截图要求里缺失的第 4 项——模型实际运行中的
推理速度（tok/s），以及真实的模型输出日志、运行截图。

用法（在本机、已联网、已装 Ollama 的 Windows/Linux/Mac 上）：

    cd lsa_C4D_Agent技能
    pip install -r requirements.txt
    python ../finalize_evidence.py

脚本会自动：
  1) 检测 Ollama 是否可用
  2) 拉取 gemma4:e4b（若缺失）
  3) 运行 agent.py 端到端流水线（function calling + 结构化输出 + 渲染地图）
  4) 用 ollama run --verbose 采集真实 tok/s 到 evidence_toks.txt
  5) 汇总产出 evidence/ 目录下的补全证据清单
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

SKILL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lsa_C4D_Agent技能")
MODEL = "gemma4:e4b"
EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lsa_C4D_output_screenshots")


def run(cmd: str, cwd: str | None = None, timeout: int = 1800) -> tuple[int, str]:
    print(f"\n$ {cmd}")
    p = subprocess.run(cmd, shell=True, cwd=cwd, text=True,
                       capture_output=True, timeout=timeout)
    out = (p.stdout or "") + (p.stderr or "")
    print(out[-2000:])
    return p.returncode, out


def main() -> int:
    print("=" * 70)
    print("C4D 证据一键补全脚本")
    print(f"目标模型：{MODEL} ｜ 时间：{datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 70)

    # 1) 检测 Ollama
    rc, _ = run("ollama --version", timeout=30)
    if rc != 0:
        print("\n[错误] 未检测到 Ollama，请先安装：https://ollama.com/download")
        return 1

    # 2) 拉取模型（若缺失）
    rc, out = run("ollama list", timeout=30)
    if MODEL not in out:
        print(f"\n[信息] 未发现 {MODEL}，开始拉取（约 4.6 GB，视网速而定）...")
        rc, _ = run(f"ollama pull {MODEL}")
        if rc != 0:
            print("\n[错误] 模型拉取失败，请检查网络后重试。")
            return 1

    # 3) 运行 agent.py 端到端流水线
    rc, out = run("python agent.py", cwd=SKILL_DIR)
    if rc != 0:
        print("\n[错误] agent.py 运行失败，输出见上。")
        return 1

    # 4) 采集真实 tok/s（评审要求的「推理速度」证据）
    prompt = "List 8 notable locations at or near SIAS University in JSON format."
    cmd = (f'ollama run {MODEL} --verbose "{prompt}"')
    rc, out = run(cmd, timeout=600)
    with open(os.path.join(SKILL_DIR, "evidence_toks.txt"), "w", encoding="utf-8") as f:
        f.write(f"# 采集时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write(f"# 模型：{MODEL}\n")
        f.write(f"# 命令：{cmd}\n\n")
        f.write(out)

    # 5) 汇总补全证据
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    summary = os.path.join(EVIDENCE_DIR, "00_evidence_summary.txt")
    with open(summary, "w", encoding="utf-8") as f:
        f.write("C4D 运行证据补全汇总\n")
        f.write(f"采集时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write(f"模型：{MODEL}（量化信息见 `ollama show {MODEL}`）\n\n")
        f.write("请人工截图以下内容并保存到本目录（用 04/05/06 前缀命名）：\n")
        f.write("  04_run_dialogue.png  —— `ollama run gemma4:e4b` 对话界面（含模型名）\n")
        f.write("  05_tok_s.png         —— 上方 evidence_toks.txt 中 eval rate 那一行\n")
        f.write("  06_map.png           —— 浏览器打开 lsa_C4D_map.html 的效果图\n")
        f.write("\ntok/s 证据已写入 agent-skill/evidence_toks.txt，其中 eval rate 即推理速度。\n")

    print("\n" + "=" * 70)
    print("✅ 证据补全完成：")
    print(f"   - 真实模型输出日志：{SKILL_DIR}/_model_raw_output.txt")
    print(f"   - tok/s 证据：       {SKILL_DIR}/evidence_toks.txt")
    print(f"   - 补全指引：         {summary}")
    print("请按 00_evidence_summary.txt 完成 3 张运行截图后，提交即完整。")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
