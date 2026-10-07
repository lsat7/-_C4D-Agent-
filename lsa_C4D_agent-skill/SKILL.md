---
name: sias-campus-map
description: >-
  本地大模型（Gemma 4 / Ollama）驱动的 Agent 技能：用 function calling 与结构化输出
  生成 SIAS University（郑州西亚斯学院）周边的交互式地图。数据由本地模型生成，不依赖云端 API。
version: 1.0.0
author: lsa
tags: [local-llm, agent, gemma4, ollama, map, leaflet, function-calling]
---

# SIAS 校园周边交互式地图技能

## 简介

这是一个运行在**本地设备**上的 LLM Agent 技能。它调用本地 Ollama 上的
Gemma 4 模型，通过**原生函数调用（function calling）**与**结构化 JSON 输出**，
生成 SIAS University 周边的地点数据，并渲染为 Leaflet 交互式 HTML 地图。

核心价值：数据不出本机、零 API 费用、可离线复现。

## 目录结构

```
lsa_C4D_agent-skill/
├── SKILL.md            # 本文件：技能说明
├── agent.py            # Agent 主循环（function calling + 结构化输出 + 渲染）
├── tools.py            # 工具定义与 JSON Schema 注册表
├── map_renderer.py     # Leaflet 交互式地图渲染器
├── config.py           # 全局配置（模型、量化、端点、中心坐标）
├── requirements.txt    # Python 依赖
└── README.md           # 详细使用说明
```

## 快速开始

```bash
# 0. 前置：本机已安装并启动 Ollama，且已拉取模型
ollama pull gemma4:e4b

# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 运行端到端演示
python agent.py
```

运行结束后，在当前目录得到 `lsa_C4D_map.html`，用浏览器打开即可查看交互式地图。

## Agent 能力

- **函数调用（function calling）**：模型自主选择并调用 `get_place_geo` /
  `search_nearby_places` / `render_interactive_map` 三个工具。
- **多步推理**：`推理 → 调工具 → 观察结果 → 再推理` 的多轮循环。
- **结构化输出**：模型以严格 JSON 数组输出地点数据，供地图渲染。
