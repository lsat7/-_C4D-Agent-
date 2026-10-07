# lsa 的 C4D 提交包 —— 本地大模型 Agent 技能（Gemma 4）

> 挑战 ID：ch-20260717031455-uzqs9k ｜ 作者（姓名）：lsa ｜ 提交日期：2026-10-07
> 一句话：在本地设备上用 Gemma 4（E4B/Q4_K_M）驱动 Agent，函数调用 + 结构化输出
> 生成 SIAS University（郑州西亚斯学院）周边交互式地图，全程不依赖云端 API。

---

## 1. 快速导览（30 秒看懂本提交）

```
想直接看效果   → 双击 lsa_C4D_map.html（8 个可点击标记 + 图例 + 可缩放）
想自己跑一遍   → 读 lsa_C4D_教学说明.md（8 步核对清单 + FAQ）
想看技术方案   → 读 lsa_C4D_方案设计.md（架构图 + 选型依据）
想核对真实性   → 读 lsa_C4D_验证报告.md（已验证项 / 未竟项如实分开）
想看 AI 怎么用 → 读 lsa_C4D_AI日志.md（7 轮迭代全留痕）
想看复盘       → 读 lsa_C4D_AAR.md（失败经验 + 改进方案）
想看加分项     → 读 lsa_C4D_uncensored对比报告.md（协议 + 脚本 + 责任讨论）
```

## 2. 交付物清单（对照挑战《需要提交什么》）

| # | 挑战要求 | 本包文件 | 说明 |
|---|---|---|---|
| 1 | 姓名_C4D_方案设计.md | `lsa_C4D_方案设计.md` | 架构、设备信息、E4B 选型理由 |
| 2 | 姓名_C4D_agent-skill/ | `lsa_C4D_agent-skill/` | 完整技能代码（含 Git 仓库 6 个规范提交） |
| 3 | 姓名_C4D_map.html | `lsa_C4D_map.html` | Leaflet 交互式地图（8 标记点） |
| 4 | 姓名_C4D_output_screenshots/ | `lsa_C4D_output_screenshots/` | 3 张真实截图（设备信息/地图/代码），推理运行截图待本机补全（见待补全清单） |
| 5 | 姓名_C4D_验证报告.md | `lsa_C4D_验证报告.md` | 质量评估 + 性能数据 + 未竟项如实说明 |
| 6 | 姓名_C4D_教学说明.md | `lsa_C4D_教学说明.md` | 安装/复现/FAQ/进阶玩法 |
| 7 | 姓名_C4D_AI日志.md（必须） | `lsa_C4D_AI日志.md` | AI 使用全过程（7 轮迭代） |
| 8 | 姓名_C4D_拿来说明.md | `lsa_C4D_拿来说明.md` | 库/工具/参考资料清单 |
| 9 | AAR（challenge.json 要求） | `lsa_C4D_AAR.md` | 复盘：做了什么/学到什么/怎么验证 + 失败经验 |
| 10 | 加分项：Uncensored 对比 | `lsa_C4D_uncensored对比报告.md` | 负责任的对比协议 + 一键脚本 |
| 11 | Level 2「模型输出日志」 | `lsa_C4D_模型输出日志.md` | 日志载体 + Prompt + 回填区（真实输出待本机运行生成） |
| 12 | 运行证据补全 | `lsa_C4D_待补全清单.md` + `finalize_evidence.py` | 缺口清单 + 15 分钟一键补全路径 |

## 3. 关键信息卡（评审速查）

| 项 | 值 |
|---|---|
| 模型 | **Gemma 4 E4B**（`gemma4:e4b`，~4.5B effective） |
| 量化 | **Q4_K_M**（4-bit，约 4.6 GB） |
| 运行时 | **Ollama v0.40.0**（OpenAI 兼容 API + 原生 tools） |
| 设备 | DESKTOP-MDK1N4L：i5-11300H（4C/8T）· 16GB RAM · Iris Xe（纯 CPU）· Windows 11 |
| Agent 能力 | function calling（3 工具）· 多步推理 · 结构化 JSON · 跨会话记忆 |
| 地图 | 8 标记点 · 五类着色 · 图例 · 可缩放/点击弹窗 |
| 完成级别 | 代码与产物齐备至 **Level 3**（函数调用/结构化输出/多步推理/记忆/技能包）；**运行证据（运行截图·tok/s·演示录屏）因沙箱网络受限待本机 15 分钟补全**，Level 4 的 Uncensored 为协议稿 + 一键脚本 |

> ⚠️ 诚实声明：本会话所在沙箱网络强限速（实测 GitHub 36 KB/s、模型仓库 0.9 KB/s），
> 多 GB 模型权重未能在会话内完成拉取，推理实测项（tok/s）未产出，**未伪造任何运行截图**。
> 缺口与 15 分钟补全步骤见《lsa_C4D_待补全清单.md》（含一键脚本 `finalize_evidence.py`）；
> 失败分析见《lsa_C4D_AAR.md》。

## 4. 目录结构

```
c4d/
├── README.md                        ← 本文件
├── finalize_evidence.py             ← 一键补全运行证据脚本（本机运行）
├── lsa_C4D_方案设计.md
├── lsa_C4D_agent-skill/             ← 技能代码（Git 仓库）
│   ├── SKILL.md  README.md
│   ├── agent.py  tools.py  memory.py  map_renderer.py  config.py
│   ├── model_output_locations.json  requirements.txt  .gitignore
│   └── .git/                        ← 6 个规范提交
├── lsa_C4D_map.html
├── lsa_C4D_output_screenshots/
│   ├── 01_device_info.png
│   ├── 02_map_screenshot.png
│   └── 03_agent_skill_code.png
├── lsa_C4D_验证报告.md
├── lsa_C4D_教学说明.md
├── lsa_C4D_模型输出日志.md           ← Level 2「模型输出日志」交付物
├── lsa_C4D_待补全清单.md            ← 运行证据缺口 + 15 分钟补全步骤
├── lsa_C4D_AI日志.md
├── lsa_C4D_拿来说明.md
├── lsa_C4D_AAR.md
└── lsa_C4D_uncensored对比报告.md
```
