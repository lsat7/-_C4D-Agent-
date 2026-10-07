"""C4D 本地 Agent 技能 —— Agent 主循环。

实现一个「本地大模型驱动的多步 Agent」：
1. 接收自然语言指令（如：给我生成一个 SIAS University 周边的地图）
2. 通过 Ollama 的 OpenAI 兼容接口调用本地 Gemma 4 模型
3. 模型在对话中自主发起 function call（工具调用），Agent 执行工具并把结果
   回填给模型，形成多轮「推理 → 调用工具 → 观察结果 → 再推理」的循环
4. 最终由模型产出结构化 JSON 地点数据，再调用渲染工具生成交互式地图

本文件同时封装了两种 Agent 能力演示路径：
   - run_tool_calling_agent()：原生 function calling 多步推理
   - generate_structured_json()：结构化 JSON 输出（地图数据主路径）
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import requests

import config
import memory as memory_mod
import tools


# ---------------------------------------------------------------------------
# 底层：调用本地 Ollama（OpenAI 兼容 /v1/chat/completions）
# ---------------------------------------------------------------------------

def call_llm(messages: List[Dict[str, Any]],
             tools_spec: Optional[List[Dict[str, Any]]] = None,
             temperature: float = config.DEFAULT_TEMPERATURE,
             max_tokens: int = config.DEFAULT_MAX_TOKENS) -> Dict[str, Any]:
    """向本地 Ollama 发起一次对话补全请求，返回完整响应 JSON。"""
    payload: Dict[str, Any] = {
        "model": config.OLLAMA_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if tools_spec:
        payload["tools"] = tools_spec
    resp = requests.post(config.OLLAMA_CHAT_ENDPOINT, json=payload,
                         timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# 路径 A：原生 function calling 多步 Agent
# ---------------------------------------------------------------------------

def run_tool_calling_agent(user_instruction: str,
                           mem: Optional["memory_mod.Memory"] = None) -> List[Dict[str, Any]]:
    """运行带工具调用的多步 Agent，返回所有工具调用记录。

    mem 参数传入 Memory 实例时，会把跨会话历史记忆注入 system prompt，
    使模型「记得」之前生成过哪些地点，体现 Agent 的记忆能力。
    """
    memory_block = mem.recall_summary() if mem else "（未启用记忆）"
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": (
            "你是一个本地运行的地理信息 Agent，运行在用户自己的电脑上（Ollama + Gemma 4）。"
            "你可以调用提供的函数来查询地点、搜索周边候选地点、渲染地图。"
            "请一步步推理：先查询/搜索，再组织数据，最后渲染地图。\n"
            f"[跨会话记忆]\n{memory_block}"
        )},
        {"role": "user", "content": user_instruction},
    ]

    tool_log: List[Dict[str, Any]] = []
    for _round in range(6):  # 最多 6 轮，防止死循环
        resp = call_llm(messages, tools_spec=tools.TOOL_SCHEMAS)
        choice = resp["choices"][0]["message"]
        messages.append(choice)

        # 模型未发起工具调用 => 对话结束
        if not choice.get("tool_calls"):
            break

        # 逐个执行模型请求的工具调用
        for tc in choice["tool_calls"]:
            fn_name = tc["function"]["name"]
            fn_args = json.loads(tc["function"].get("arguments", "{}"))
            result = tools.TOOL_DISPATCH[fn_name](**fn_args)
            tool_log.append({
                "round": _round + 1,
                "tool": fn_name,
                "arguments": fn_args,
                "result": result,
            })
            # 把工具执行结果作为 tool 消息回填
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", "call_0"),
                "content": json.dumps(result, ensure_ascii=False),
            })

    return tool_log


# ---------------------------------------------------------------------------
# 路径 B：结构化 JSON 输出（地图数据主路径）
# ---------------------------------------------------------------------------

STRUCTURED_PROMPT = """你是本地运行的地理助手。请列出 SIAS University（郑州西亚斯学院，位于河南新郑）校园及周边 8 个有代表性的地点。

严格要求：
1. 只输出一个合法的 JSON 数组，不要输出任何其他文字、解释或 Markdown 代码块标记。
2. 数组每一项是一个对象，字段如下：
   - name: 英文名（string）
   - name_zh: 中文名（string）
   - latitude: 纬度（number，float）
   - longitude: 经度（number，float）
   - description: 一句话描述（string，中英双语均可）
3. 坐标必须围绕郑州西亚斯学院（约 34.40, 113.73）附近，误差在 1 度以内。
4. 必须包含 SIAS University 本身作为第一个元素。"""


def generate_structured_json() -> List[Dict[str, Any]]:
    """用本地模型生成结构化地点 JSON（地图数据来源，非手写）。"""
    messages = [
        {"role": "system", "content": "You are a geography assistant. Always respond with valid JSON only."},
        {"role": "user", "content": STRUCTURED_PROMPT},
    ]
    resp = call_llm(messages, temperature=0.2, max_tokens=2048)
    content = resp["choices"][0]["message"]["content"]
    # 记录原始输出（用于 AI 日志 / 验证报告）
    with open("_model_raw_output.txt", "w", encoding="utf-8") as f:
        f.write(content)
    # 清理可能出现的代码块围栏
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        content = content.lstrip("json").strip()
    data = json.loads(content)
    if isinstance(data, dict) and "locations" in data:
        data = data["locations"]
    return data


# ---------------------------------------------------------------------------
# 端到端主流程
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("C4D 本地大模型 Agent 技能 —— 端到端演示")
    print(f"模型：{config.OLLAMA_MODEL}（{config.MODEL_QUANT}） @ {config.OLLAMA_BASE_URL}")
    print("=" * 70)

    # 0) 加载跨会话记忆
    mem = memory_mod.Memory()
    print(f"\n[Step 0] 加载记忆：{len(mem.records)} 条历史记录")

    # 1) 多步 Agent（function calling）演示
    print("\n[Step 1] 运行 function calling 多步 Agent ...")
    t0 = time.time()
    instruction = "给我生成一个 SIAS University 周边的地图，先搜索周边地点，再渲染成交互式地图。"
    tool_log = run_tool_calling_agent(instruction, mem=mem)
    print(f"        完成，共触发 {len(tool_log)} 次工具调用，耗时 {time.time()-t0:.1f}s")
    for item in tool_log:
        print(f"        - 工具 {item['tool']}，参数 {json.dumps(item['arguments'], ensure_ascii=False)}")

    # 2) 结构化 JSON 输出（生成地图数据）
    print("\n[Step 2] 生成结构化地点数据（由本地模型生成） ...")
    t0 = time.time()
    points = generate_structured_json()
    print(f"        完成，共 {len(points)} 个地点，耗时 {time.time()-t0:.1f}s")
    for p in points:
        print(f"        - {p.get('name_zh', p.get('name'))} ({p.get('latitude')}, {p.get('longitude')})")

    # 3) 渲染交互式地图
    print("\n[Step 3] 渲染 Leaflet 交互式地图 ...")
    result = tools.render_interactive_map(
        points,
        output_path=config.MAP_OUTPUT,
        center=[config.CENTER_LAT, config.CENTER_LNG],
        zoom=config.MAP_ZOOM,
    )
    print(f"        地图已生成：{result['output_path']}（标记点 {result['markers']} 个）")

    # 4) 保存结构化数据供审计 + 写入记忆
    with open("_model_locations.json", "w", encoding="utf-8") as f:
        json.dump(points, f, ensure_ascii=False, indent=2)
    with open("_tool_call_log.json", "w", encoding="utf-8") as f:
        json.dump(tool_log, f, ensure_ascii=False, indent=2)

    mem.remember(
        instruction=instruction,
        places=points,
        tools_used=[item["tool"] for item in tool_log] or ["generate_structured_json"],
        extra={"model": config.OLLAMA_MODEL, "quant": config.MODEL_QUANT},
    )
    print(f"\n[Step 4] 已写入记忆（当前共 {len(mem.records)} 条历史记录）")

    print("\n✅ 全部完成。请用浏览器打开 lsa_C4D_map.html 查看交互式地图。")


if __name__ == "__main__":
    main()
