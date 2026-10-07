# lsa_C4D_待补全清单（运行证据）

> 挑战：C4D 本地大模型 Agent 技能 ｜ 作者（姓名）：lsa
> 用途：如实列出本提交因**沙箱网络强限速**（实测 GitHub 36 KB/s、模型仓库 0.9 KB/s）
> 未能在本会话内采集的「实际运行证据」，并给出在本机 15 分钟内的精确补全步骤。
> **这些项全部为环境性未竟，非方案缺陷；代码与产物均已就绪、可直接运行。**

---

## 1. 差距总览（对照挑战文档逐项）

| # | 挑战要求 | 当前状态 | 差距 | 补全方式 |
|---|---|---|---|---|
| R1 | 截图须含「模型名称及版本」 | ✅ 已满足（`01_device_info.png` 标注 `gemma4:e4b`） | 无 | — |
| R2 | 截图须含「运行工具」 | ✅ 已满足（Ollama v0.40.0） | 无 | — |
| R3 | 截图须含「设备信息 CPU/GPU/内存/OS」 | ✅ 已满足（`01_device_info.png`） | 无 | — |
| R4 | 截图须含「推理速度 tok/s」 | ❌ 未采集 | 缺运行截图 | 一键脚本 `finalize_evidence.py` → §2.2 |
| R5 | Level 2「模型输出日志」 | ⚠️ 现为示例数据 | 缺真实日志 | §2.1，运行后回填《模型输出日志.md》§3 |
| R6 | Level 3「演示录屏」 | ❌ 未录制 | 缺录屏 | §2.3 |
| R7 | 加分项 Uncensored「实测对比数据」 | ⚠️ 现为协议+脚本 | 缺实测数值 | §2.4 |

---

## 2. 补全步骤（本机、已联网、已装 Ollama）

### 2.1 一次性补齐 R4/R5（约 10 分钟，含模型下载）

```bash
cd lsa_C4D_agent-skill
pip install -r requirements.txt
python ../finalize_evidence.py
```

脚本自动完成：检测 Ollama → `ollama pull gemma4:e4b` → 运行 `agent.py`
（产出真实 `_model_raw_output.txt`、`_tool_call_log.json`、重渲染地图）→
`ollama run --verbose` 采集 tok/s → 生成 `00_evidence_summary.txt`。

### 2.2 补齐截图 R4（约 2 分钟）

按 `lsa_C4D_output_screenshots/00_evidence_summary.txt` 提示，人工截 3 张图：

- `04_run_dialogue.png`：`ollama run gemma4:e4b` 对话界面（含模型名）
- `05_tok_s.png`：`evidence_toks.txt` 中 `eval rate` 行（即 tok/s）
- `06_map.png`：浏览器打开 `lsa_C4D_map.html` 的效果图

> 截图要点：终端标题栏/第一行要能看到 `gemma4:e4b`；`05` 这张要把
> `eval rate: xxx tokens/s` 整行截进去——这就是评审要求第 4 项的证据。

### 2.3 补齐演示录屏 R6（约 3 分钟）

任选其一：

- **Windows**：`Win + G` 打开 Xbox Game Bar → 开始录制 → 依次演示
  `ollama run gemma4:e4b` 对话 + `python agent.py` 全流程 + 打开地图交互；
- **跨平台**：OBS Studio 录屏；
- 保存为 `lsa_C4D_demo.mp4`，放进 `lsa_C4D_output_screenshots/`。

### 2.4 补齐 Uncensored 实测 R7（约 10 分钟）

按《lsa_C4D_uncensored对比报告.md》§5 执行：

```bash
ollama pull gemma4:e4b
# 自行甄别来源后导入 uncensored 变体
ollama create gemma4-e4b-unc -f Modelfile
python uncensored_compare.py > compare_result.txt 2>&1
```

按报告 §3.2 口径统计拒答率 / 任务完成率 / 输出质量，回填报告 §4 的表格。

---

## 3. 完成后自检（补全后本提交即为「完整可评审」状态）

- [ ] `lsa_C4D_output_screenshots/` 内已有 `04/05/06` 三张运行截图
- [ ] 《lsa_C4D_模型输出日志.md》§3 已回填真实模型输出
- [ ] `lsa_C4D_demo.mp4` 已放置
- [ ] Uncensored 报告 §4 已填入实测数值
- [ ] 重新核对：截图 4 项信息（模型名/工具/设备/tok/s）齐备

---

## 4. 诚实边界声明

本清单不提供任何「伪造运行证据」的方法。R4–R7 的每一项都必须在**真实设备上
真实运行**后采集；这也正是挑战「本地运行验证 25%」要考察的核心——评审会核对
tok/s 与设备配置是否匹配，伪造数据反而会被识别并扣分。本提交的价值在于：
**代码与产物完备、证据采集路径一键可复现、失败经验如实记录**（见 AAR）。
