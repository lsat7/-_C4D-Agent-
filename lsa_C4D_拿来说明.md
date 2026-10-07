# lsa_C4D_拿来说明

> 挑战：C4D 本地大模型 Agent 技能 ｜ 作者：lsa ｜ 日期：2026-10-07
> 说明本文回答两个问题：**用了哪些库/工具**、**参考了什么资料**。

---

## 1. 直接依赖的库与工具

### 1.1 模型与运行时

| 名称 | 版本/规格 | 用途 | 许可 |
|---|---|---|---|
| Gemma 4 E4B | `gemma4:e4b`，Q4_K_M 量化（约 4.6 GB），~4.5B effective | 本地推理引擎（函数调用/结构化输出） | Apache 2.0（Google 开源） |
| Ollama | v0.40.0（Windows 便携版） | 本地模型服务，提供 OpenAI 兼容 API `/v1/chat/completions` 与原生 `tools` 参数 | MIT |

### 1.2 Python 依赖（仅 1 个第三方库）

| 库 | 用途 | 许可 |
|---|---|---|
| requests ≥ 2.31 | 调用本地 Ollama HTTP API | Apache 2.0 |

其余全部为 Python 标准库：`json`、`time`、`os`、`typing`——
依赖极简是为了「别人照教学说明一定能跑通」（可复用性 15%）。

### 1.3 前端与地图

| 名称 | 用途 | 许可 |
|---|---|---|
| Leaflet.js 1.9.4（unpkg CDN） | 交互式地图引擎：缩放/拖拽/标记/弹窗/提示 | BSD-2-Clause |
| OpenStreetMap 瓦片 | 地图底图 | ODbL（署名-相同方式共享） |

### 1.4 工程与核验工具

| 工具 | 用途 |
|---|---|
| Git | 技能包版本管理（6 个规范提交） |
| Chrome 无头模式（`--headless --screenshot`） | 地图/文档渲染截图核验 |
| Python `py_compile` | 全模块语法验证 |
| Git Bash / PowerShell | 命令执行环境 |

---

## 2. 参考资料

### 2.1 挑战官方材料（一手依据）

| 资料 | 用途 |
|---|---|
| `CHALLENGE.md` | 任务目标、四级任务、交付清单、评审五维、加分项定义 |
| `materials/C4D.pdf` | 与 CHALLENGE.md 同源正式版（10 页），交叉核对交付物清单 |
| `materials/C4D 补充说明.pdf` | 非 CS 专属通道说明（三步完成法），用作背景理解 |
| `rubric.json` + `challenge.json` | 第二套结构化评分维度（含「有记忆」「Git 提交清晰」等信号）与红旗项 |
| `challenge.yaml` | 交付物 pattern：`*Agent技能*,*demo*,*AI日志*,*AAR*` |

### 2.2 官方文档（写代码时对照）

| 资料 | 用途 |
|---|---|
| [Ollama 官方文档](https://ollama.com) / `ollama show`、`ollama list` 命令 | 模型拉取、量化信息查询 |
| [Ollama OpenAI 兼容 API](https://ollama.com) `/v1/chat/completions` | `tools` 参数与 `tool_calls` 响应结构（agent.py 的调用契约） |
| [Leaflet 官方文档](https://leafletjs.com/) | `circleMarker`/`bindPopup`/`bindTooltip`/`tileLayer` 用法 |
| [Folium 文档](https://python-visualization.github.io/folium/) | 对比后弃用（Leaflet 纯前端更符合「双击即开」），架构决策依据 |

### 2.3 挑战文档给出的参考资源

| 资源 | 用途 |
|---|---|
| [Ollama Gemma 4 页面](https://ollama.com/library/gemma4) | 确认 `e2b/e4b/26b/31b` 及 `-it-q4_K_M` 等变体真实存在与体量 |
| [Gemma 4 官方博客](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) | 四款模型定位与能力（多模态/函数调用/结构化输出） |
| [Unsloth Gemma 4 本地运行指南](https://unsloth.ai/docs/models/gemma-4) | 硬件需求对照 |
| [AI Edge Gallery](https://ai.google.dev/edge) | 手机端方案（本方案未用，列入教学说明备选） |

---

## 3. 明确「没有用」的东西（避免误解）

- **未使用任何云端 LLM API**（OpenAI/Claude/文心等）参与技能运行时——
  技能运行时只调用 `http://localhost:11434` 本机服务，数据不出本机；
- 未使用 LangChain/LlamaIndex 等重框架——Agent 循环仅 ~50 行自实现，
  避免黑盒、便于评审；
- 未手写地图坐标进代码——地点数据独立存放于
  `model_output_locations.json`（模型输出产物），渲染器只读数据。

---

## 4. 致谢与许可声明

- 感谢 Google 开源 Gemma 4（Apache 2.0）、Ollama（MIT）、Leaflet（BSD-2-Clause）、
  OpenStreetMap 贡献者（ODbL）；
- 本提交所有文档与代码由 lsa 组织完成，AI（WorkBuddy）作为结对工程工具全程留痕
  （见《lsa_C4D_AI日志.md》）。
