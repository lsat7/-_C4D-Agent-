# lsa_C4D_模型输出日志

> 挑战：C4D 本地大模型 Agent 技能 ｜ 作者（姓名）：lsa
> 对应交付项：Level 2「交互式地图 HTML + 生成地图的完整代码 + **模型输出日志**」

---

## 0. 本文件的定位（诚实说明）

本文件是「模型输出日志」这一交付物的**载体与结果记录**。

- 技能主程序 `agent.py` 在运行时会把本地 `gemma4:e4b` 的**原始输出**写入
  `_model_raw_output.txt`（代码见 `agent.py:generate_structured_json` 第 132 行）；
- **§3 已填入真实模型输出**——2026-10-07 在本机 DESKTOP-MDK1N4L 上，
  用 `llama-cpp-python` CPU 后端直接加载经 SHA256 校验的 `gemma4:e4b` 权重运行采集；
- 采集脚本：`work/c4d/run_real_inference.py`；原始结果：
  `work/c4d/evidence/run_A_raw_output.txt` 与 `real_inference_result.json`。

> 说明：本次实测使用 llama-cpp-python 直接加载同一份权重（因交付会话无法拉取
> 1.4 GB 的 Ollama 运行时）。prompt 与 `agent.py` 的 `STRUCTURED_PROMPT` **完全一致**，
> 因此输出可代表该模型在本任务上的真实表现。

---

## 1. 发送给模型的完整 Prompt（真实，来自 agent.py）

```text
system: You are a geography assistant. Always respond with valid JSON only.

user: 你是本地运行的地理助手。请列出 SIAS University（郑州西亚斯学院，位于河南新郑）校园及周边 8 个有代表性的地点。

严格要求：
1. 只输出一个合法的 JSON 数组，不要输出任何其他文字、解释或 Markdown 代码块标记。
2. 数组每一项是一个对象，字段如下：
   - name: 英文名（string）
   - name_zh: 中文名（string）
   - latitude: 纬度（number，float）
   - longitude: 经度（number，float）
   - description: 一句话描述（string，中英双语均可）
3. 坐标必须围绕郑州西亚斯学院（约 34.40, 113.73）附近，误差在 1 度以内。
4. 必须包含 SIAS University 本身作为第一个元素。
```

---

## 2. 预期输出格式（示例数据，供对照 schema）

```json
[
  {
    "name": "SIAS University",
    "name_zh": "郑州西亚斯学院",
    "latitude": 34.4005,
    "longitude": 113.7302,
    "description": "……"
  }
]
```

> 完整示例见 `model_output_locations.json`（8 条，含 category 扩展字段，
> category 由渲染器使用、非模型必填）。

---

## 3. 真实模型输出（2026-10-07 本机实测）

**运行环境**：`gemma4:e4b`（Ollama registry 权重，SHA256 已校验 `370c2879f17648…`）
· `llama-cpp-python` 0.3.36 CPU 后端 · `n_ctx=4096` · `n_threads=4` · `n_gpu_layers=0`
· 设备 DESKTOP-MDK1N4L（i5-11300H / 16 GB / Iris Xe）

**采集参数**：`temperature=0.2`、`max_tokens=900`
**实测性能**：生成 624 tokens / 85.41 s = **7.31 tok/s**

模型原始输出（未经任何人工修改，含模型自行添加的 Markdown 围栏）：

```json
[
  {
    "name": "SIAS University",
    "name_zh": "郑州西亚斯学院",
    "latitude": 34.4012,
    "longitude": 113.7315,
    "description": "The main campus of SIAS University, located in Xinzheng, Zhengzhou."
  },
  {
    "name": "Xinzheng City Center",
    "name_zh": "新郑市中心",
    "latitude": 34.4150,
    "longitude": 113.7250,
    "description": "The central commercial and administrative area of Xinzheng City."
  },
  {
    "name": "Zhengzhou Railway Station",
    "name_zh": "郑州火车站",
    "latitude": 34.7590,
    "longitude": 113.6420,
    "description": "A major transportation hub in Zhengzhou, serving as a key regional link."
  },
  {
    "name": "Henan Provincial Museum",
    "name_zh": "河南省博物馆",
    "latitude": 34.7610,
    "longitude": 113.7100,
    "description": "A significant cultural site showcasing the history and heritage of Henan Province."
  },
  {
    "name": "Xinzheng Industrial Zone",
    "name_zh": "新郑工业园区",
    "latitude": 34.3900,
    "longitude": 113.7500,
    "description": "The primary industrial development area near the university."
  },
  {
    "name": "Local Market Area",
    "name_zh": "本地集市区域",
    "latitude": 34.4050,
    "longitude": 113.7380,
    "description": "A vibrant local market where students and residents shop for daily necessities."
  },
  {
    "name": "Jiaozuo Town",
    "name_zh": "焦作镇",
    "latitude": 34.3800,
    "longitude": 113.7150,
    "description": "A nearby town providing local community services and residential areas."
  },
  {
    "name": "Gongyuan Park",
    "name_zh": "公园绿地",
    "latitude": 34.4000,
    "longitude": 113.7350,
    "description": "A local park offering recreational space for the campus community."
  }
]
```

### 3.1 输出质量如实评估

| 校验项 | 标准 | 实测结果 |
|---|---|---|
| JSON 可解析 | `json.loads` 通过 | ⚠️ 需先剥离 Markdown 围栏（`agent.py` 已内置清理逻辑，见第 136–138 行） |
| 数组长度 | 8 条 | ✅ 8 条 |
| 必填字段齐全 | name / name_zh / latitude / longitude / description | ✅ 8/8 条齐全 |
| 首元素为中心点 | 第 1 条为 SIAS University | ✅ 符合 |
| 坐标在合理范围 | 距 (34.40, 113.73) 偏差 ≤ 1° | ✅ 8/8 条均在范围内 |

**观察到的真实局限（如实记录，不做美化）**：

1. **模型添加了 Markdown 围栏** —— prompt 明确要求"不要输出 Markdown 代码块标记"，
   模型仍加了 ` ```json `，证明小模型的指令遵从并非 100%，工程上必须做输出清洗。
2. **部分地名存在事实偏差** —— 例如 `Jiaozuo Town`（焦作镇）的描述为"附近的城镇"，
   但焦作市实际位于郑州西北约 80 km，并非紧邻西亚斯学院的城镇；
   `Xinzheng Industrial Zone`、`Local Market Area` 属模型泛化生成的通用名称，
   非确切地名。这提示：**本地小模型的地理知识适合做"草稿"，落地前需人工核验**。
3. **坐标为近似值** —— 模型给出的坐标是围绕中心点的合理推测，
   与真实 POI 存在偏差（如 Henan Provincial Museum 实际约 34.79, 113.66）。

> 上述局限正是本提交把 `model_output_locations.json` 作为**经人工核验的数据**
> 交付、而非直接采用模型原始输出的原因——即「模型出草稿 + 人工做校验」的
> 数据可信链路。这也是 AAR 中记录的改进方向之一。

---

## 4. 与其它交付物的关系

| 文件 | 作用 |
|---|---|
| `work/c4d/evidence/run_A_raw_output.txt` | 本文件 §3 的**原始来源**（模型原始输出） |
| `work/c4d/evidence/real_inference_result.json` | 三次运行的完整实测数据（tokens/耗时/tok·s⁻¹） |
| `model_output_locations.json` | 经**人工核验**后的结构化数据（渲染地图的直接输入） |
| `_tool_call_log.json`（运行后生成） | function calling 的工具调用轨迹 |
| `evidence_toks.txt`（运行后生成） | 推理速度 tok/s 证据（截图要求第 4 项） |

> 💡 在装有 Ollama 的环境执行 `python agent.py` 后，本机还会额外产出
> `_model_raw_output.txt`，可与 §3 交叉比对。
