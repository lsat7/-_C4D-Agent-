# lsa_C4D_模型输出日志

> 挑战：C4D 本地大模型 Agent 技能 ｜ 作者（姓名）：lsa
> 对应交付项：Level 2「交互式地图 HTML + 生成地图的完整代码 + **模型输出日志**」

---

## 0. 本文件的定位（诚实说明）

本文件是「模型输出日志」这一交付物的**载体与格式定义**。

- 技能主程序 `agent.py` 在运行时会把本地 `gemma4:e4b` 的**原始输出**写入
  `_model_raw_output.txt`（代码见 `agent.py:generate_structured_json` 第 132 行）；
- 当前 `model_output_locations.json` 为**示例数据**——由本会话 AI 按真实坐标生成、
  用于地图渲染与字段 schema 验证，**并非 `gemma4:e4b` 的实测输出**；
- 在具备正常网络的本机执行一次 `python agent.py`（或一键脚本
  `finalize_evidence.py`）后，`_model_raw_output.txt` 即成为真实日志，
  届时把其内容粘贴到本文 §3 的「真实输出回填区」即可。

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

## 3. 真实输出回填区（本机运行后粘贴）

```
【待回填】在本机执行 `python agent.py` 后，把 _model_raw_output.txt 的内容
粘贴到这里。此即 Level 2 要求的真实「模型输出日志」。
```

---

## 4. 与其它交付物的关系

| 文件 | 作用 |
|---|---|
| `_model_raw_output.txt`（运行后生成） | 模型**原始**输出（本日志的真实来源） |
| `model_output_locations.json` | 解析后的结构化数据（渲染地图的直接输入） |
| `_tool_call_log.json`（运行后生成） | function calling 的工具调用轨迹 |
| `evidence_toks.txt`（运行后生成） | 推理速度 tok/s 证据（截图要求第 4 项） |
