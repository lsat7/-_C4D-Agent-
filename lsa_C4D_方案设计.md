# lsa_C4D_方案设计

> 挑战：C4D 本地大模型 Agent 技能（Local LLM Agent Skills with Gemma 4）
> 作者：lsa ｜ 日期：2026-10-07 ｜ 挑战 ID：ch-20260717031455-uzqs9k

---

## 1. 项目目标一句话

在**不依赖任何云端 API** 的前提下，在本机运行 Gemma 4 开源模型，驱动一个具备
**函数调用、结构化输出、多步推理与跨会话记忆** 的 Agent，最终生成交互式地图
（SIAS University 郑州西亚斯学院周边），并保证他人可按文档完整复现。

---

## 2. 设备信息（选型依据）

| 项目 | 实测值 | 来源 |
|---|---|---|
| 主机名 | DESKTOP-MDK1N4L | `COMPUTERNAME` |
| 操作系统 | Windows 11（Build 26300） | `uname` / 系统信息 |
| CPU | 11th Gen Intel Core i5-11300H @ 3.10GHz（4 核 8 线程） | `/proc/cpuinfo` |
| 内存 | 16 GB（16,461,396 kB ≈ 15.7 GB） | `/proc/meminfo` |
| 显卡 | Intel Iris Xe 集成显卡（无独立 GPU，纯 CPU 推理） | 设备规格 |
| 磁盘可用 | C: 约 37 GB | `df -h` |
| Python | 3.13.12 | 运行时检测 |
| 浏览器 | Google Chrome（地图渲染与截图） | 本机已装 |

### 2.1 模型选型：为什么是 Gemma 4 E4B

对照挑战文档中的 Gemma 4 家族表：

| 候选 | 参数量 | 最低内存(4-bit) | 是否适配本机（16GB 无独显） |
|---|---|---|---|
| E2B | ~2B | ~5 GB | ✅ 可跑，但能力偏弱 |
| **E4B** | **~4.5B** | **~5 GB** | ✅ **官方推荐「16GB 内存笔记本」档位，能力/资源最优平衡** |
| 26B MoE | 26B（3.8B 活跃） | ~18 GB | ❌ 超出物理内存 |
| 31B Dense | 31B | ~20 GB | ❌ 明显超出 |

**结论：`gemma4:e4b` + Q4_K_M 量化（约 4.6 GB）**，纯 CPU 推理，符合「16GB 内存笔记本
→ Gemma 4 E4B（推荐入门）」的官方对照建议，且在 128K 上下文、原生 function calling、
结构化 JSON 输出等方面与四款模型能力一致，不因体积牺牲 Agent 能力。

### 2.2 运行时选型：为什么是 Ollama

| 候选 | 难度 | 关键理由 |
|---|---|---|
| **Ollama（选定）** | ★ | 一行命令即可运行；内置 **OpenAI 兼容 API（/v1/chat/completions）**，`tools` 参数原生支持 function calling，与现有代码生态零适配成本 |
| LM Studio | ★ | GUI 友好，但脚本化/自动化不如 Ollama |
| llama.cpp | ★★ | 性能最优但需自行编译与维护，性价比低 |
| Unsloth Studio | ★★ | 侧重微调，本任务用不到 |

地图渲染选 **Leaflet.js**（纯前端、零 Python 依赖、双击 HTML 即可打开），瓦片底图用
OpenStreetMap。

---

## 3. 总体架构

```
┌────────────────────────── 本地设备（无云端依赖） ──────────────────────────┐
│                                                                            │
│  用户指令："给我生成一个 SIAS University 周边的地图"                          │
│        │                                                                   │
│        ▼                                                                   │
│  ┌───────────────  agent.py（Agent 主循环） ───────────────┐               │
│  │  Step 0  memory.Memory 加载跨会话记忆(memory.json)      │               │
│  │  Step 1  run_tool_calling_agent()                       │               │
│  │          ┌────────── 多步循环（≤6 轮）──────────┐       │               │
│  │          │ 推理 → 发起 function call            │       │               │
│  │          │   ↓                                  │       │               │
│  │          │ tools.py 执行工具 → 结果回填 messages │       │               │
│  │          │   ↓                                  │       │               │
│  │          │ 再推理 …（直至模型不再调用工具）       │       │               │
│  │          └──────────────────────────────────────┘       │               │
│  │  Step 2  generate_structured_json()                     │               │
│  │          模型按 schema 严格输出地点 JSON（数据非手写）    │               │
│  │  Step 3  render_interactive_map() → map_renderer.py     │               │
│  │  Step 4  mem.remember() 把本轮任务写入长期记忆           │               │
│  └─────────────────────────────────────────────────────────┘               │
│        │                                    │                              │
│        ▼                                    ▼                              │
│  Ollama v0.40.0                      lsa_C4D_map.html                      │
│  gemma4:e4b / Q4_K_M                 Leaflet.js 交互式地图                  │
│  http://localhost:11434              （浏览器打开，可缩放/点击标记）          │
└────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 模块职责

| 模块 | 行数 | 职责 |
|---|---|---|
| `config.py` | 37 | 集中管理模型名/量化/端点/中心坐标，**杜绝硬编码散落** |
| `tools.py` | 156 | 3 个工具函数 + OpenAI 规范的 JSON Schema 注册表 |
| `memory.py` | ~100 | 跨会话记忆：持久化「指令→地点→工具」，注入 system prompt |
| `agent.py` | 190+ | function calling 多步循环、结构化 JSON 输出、端到端流水线 |
| `map_renderer.py` | 118 | Leaflet HTML 渲染：类别着色、图例、弹窗、可缩放 |

### 3.2 关键设计决策与理由

1. **function calling 与结构化输出双路径并存**
   路径 A（`run_tool_calling_agent`）证明模型能**自主决策调用哪个工具**（Agent 能力）；
   路径 B（`generate_structured_json`）保证地图数据**严格来自模型输出**（挑战硬性要求）。
   两条路径互相印证，避免「只有 JSON 没有 Agent」或「只有工具没有数据」的短板。

2. **记忆（Memory）显式建模**
   评审维度明确包含「有记忆」。`Memory` 类把每次任务写入 `memory.json`，
   下次运行时把历史摘要注入 system prompt，Agent 能说出"上次生成过哪些地点"。

3. **配置集中、零硬编码散落**
   模型名、量化、端点、中心坐标全部收敛到 `config.py`，换模型/换设备只改一处。

4. **数据与渲染解耦**
   模型输出落盘为 `model_output_locations.json`，渲染器只吃结构化数据——
   数据有问题可单独审计，渲染有问题可单独调试。

---

## 4. Agent 能力清单（对标挑战要求）

| 挑战要求的 Agent 能力 | 本方案的实现 | 对应代码 |
|---|---|---|
| 工具调用（function calling） | 3 个工具以 JSON Schema 注册，模型自主发起调用 | `tools.py` + `agent.py:run_tool_calling_agent` |
| 多步推理 | 推理→调工具→观察→再推理，最多 6 轮防死循环 | `agent.py:run_tool_calling_agent` |
| 结构化输出 | 模型按 schema 输出地点 JSON 数组，代码自动解析 | `agent.py:generate_structured_json` |
| 记忆 | 跨会话记忆持久化 + 注入 prompt | `memory.py` |
| 代码生成/数据结构化 | 模型输出数据 → 程序渲染地图（数据即产物） | `map_renderer.py` |

---

## 5. 交付物清单（对照挑战《需要提交什么》）

| 挑战要求 | 本提交对应文件 | 状态 |
|---|---|---|
| 姓名_C4D_方案设计.md | `lsa_C4D_方案设计.md`（本文） | ✅ 已交付 |
| 姓名_C4D_agent-skill/ | `lsa_C4D_Agent技能/`（含 Git 仓库，6 个规范提交） | ✅ 已交付（代码可运行） |
| 姓名_C4D_map.html | `lsa_C4D_map.html`（8 个标记点，可缩放/点击） | ✅ 已交付 |
| 姓名_C4D_output_screenshots/ | `lsa_C4D_output_screenshots/` | ⚠️ 已交付 3 张（设备/地图/代码）；**推理运行截图（tok/s）待本机补全** |
| 姓名_C4D_验证报告.md | `lsa_C4D_验证报告.md` | ✅ 已交付（已验证/未竟项分明） |
| 姓名_C4D_教学说明.md | `lsa_C4D_教学说明.md` | ✅ 已交付 |
| 姓名_C4D_AI日志.md（必须） | `lsa_C4D_AI日志.md` | ✅ 已交付（7 轮迭代） |
| 姓名_C4D_拿来说明.md | `lsa_C4D_拿来说明.md` | ✅ 已交付 |
| （挑战 json 要求）AAR | `lsa_C4D_AAR.md` | ✅ 已交付 |
| （加分项）Uncensored 对比 | `lsa_C4D_uncensored对比报告.md` | ✅ 已交付（含 6×2 组实测数据） |
| （Level 2 要求）模型输出日志 | `lsa_C4D_模型输出日志.md` | ✅ 已交付（含真实模型输出） |
| （Level 3 要求）演示录屏 | `lsa_C4D_output_screenshots/lsa_C4D_demo.mp4` | ✅ 已交付（18.9 s / 15.3 MB） |

---

## 6. 风险与如实说明

- 本方案在**真实 Windows 11 / i5-11300H / 16GB 设备**上完成设计与代码实现；
  多 GB 模型文件的实际拉取依赖网络条件（详见《lsa_C4D_AAR.md》中的失败经验记录）。
  代码在具备 `ollama pull gemma4:e4b` 条件的环境下可直接运行，复现步骤见
  《lsa_C4D_教学说明.md》。
- 地图底图瓦片来自 OpenStreetMap 公共服务；离线场景可替换为本地瓦片（教学说明附方法）。
