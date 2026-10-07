# lsa_C4D_Agent技能 — 本地大模型 Agent 技能

> C4D 挑战：本地大模型 Agent 技能（Local LLM Agent Skills with Gemma 4）

本目录是一个**可复用、可独立运行**的本地 Agent 技能：调用本机 Ollama 上的
Gemma 4 模型，通过原生函数调用与结构化输出，生成 SIAS University（郑州西亚斯学院）
周边的交互式地图。

---

## 1. 这是什么

```
你的自然语言指令
      ↓
本地 Gemma 4 模型（Ollama，gemma4:e4b / Q4_K_M）
      ↓
Agent 自主 function calling：搜索周边地点 / 查询坐标 / 渲染地图
      ↓
结构化 JSON 地点数据（由模型生成，非手写）
      ↓
Leaflet 交互式 HTML 地图（可缩放、可点击标记）
      ↓
浏览器打开 → 截图/录屏
```

## 2. 运行环境（评审关键信息）

| 项目 | 值 |
|---|---|
| 模型 | `gemma4:e4b`（Gemma 4 E4B，~4.5B effective） |
| 量化 | Q4_K_M（4-bit） |
| 运行工具 | Ollama v0.40.0（OpenAI 兼容 API） |
| 设备 | DESKTOP-MDK1N4L（Intel Core i5-11300H @ 3.10GHz，4C/8T） |
| 内存 | 16 GB |
| 显卡 | Intel Iris Xe（纯 CPU 推理） |
| 系统 | Windows 11（Build 26300） |

## 3. 文件说明

| 文件 | 作用 |
|---|---|
| `agent.py` | Agent 主循环：function calling 多步推理 + 结构化输出 + 端到端渲染 |
| `tools.py` | 三个工具函数及其 JSON Schema 注册表 |
| `map_renderer.py` | Leaflet 交互式地图渲染器（纯前端 HTML） |
| `config.py` | 全局配置（模型/量化/端点/中心坐标） |
| `SKILL.md` | 技能元信息与简要说明 |
| `requirements.txt` | Python 依赖清单 |

## 4. 复现步骤

```bash
# ① 安装并启动 Ollama（Windows 下载安装包；Linux/Mac 用官方脚本）
# ② 拉取模型
ollama pull gemma4:e4b

# ③ 安装依赖
pip install -r requirements.txt

# ④ 运行
python agent.py

# ⑤ 浏览器打开 lsa_C4D_map.html
```

## 5. Agent 能力清单

- ✅ 原生 **function calling**：模型自主调用 3 个工具
- ✅ **多步推理**：推理 → 调工具 → 观察 → 再推理的循环
- ✅ **结构化 JSON 输出**：地点数据由模型严格按 schema 生成
- ✅ **代码生成 + 执行**：Agent 生成地图渲染代码并落地为 HTML

## 6. 许可与致谢

- 模型：Google Gemma 4（Apache 2.0）
- 地图库：Leaflet.js（BSD-2-Clause）；瓦片：OpenStreetMap（ODbL）
