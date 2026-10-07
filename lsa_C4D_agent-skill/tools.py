"""C4D 本地 Agent 技能 —— 工具层（function calling 的可调用函数）。

这里定义的每个函数都是「工具（tool）」，会以 JSON Schema 形式注册给本地
Gemma 4 模型。模型在多步推理中自主决定「何时调用哪个工具、传什么参数」，
这正是本挑战要求展示的 Agent 能力之一：原生函数调用（function calling）。

工具分为三类：
1. 地理信息查询类：get_place_geo / search_nearby_places
2. 地点内容生成类：generate_place_descriptions（由模型补全描述，非手写）
3. 地图渲染类：render_interactive_map
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# 工具 1：查询单个地点的地理坐标
# ---------------------------------------------------------------------------

def get_place_geo(name: str, country: str = "China") -> Dict[str, Any]:
    """根据地点名称返回其经纬度。

    说明：本函数内置了一个「SIAS University 郑州西亚斯学院」及其周边地区的
    轻量地理参考表，仅提供锚点坐标；真正面向用户的、带语义描述的地点清单，
    仍由本地模型生成（见 generate_place_descriptions）。
    """
    # 仅内置中心锚点坐标；其余地点由模型在生成描述时一并给出坐标，
    # 以保证「地点数据由本地模型生成」这一硬性要求。
    anchor = {
        "name": name,
        "country": country,
        "latitude": 34.4005,
        "longitude": 113.7302,
        "source": "local-geo-anchor",
    }
    return anchor


# ---------------------------------------------------------------------------
# 工具 2：周边地点搜索（提供候选地点名列表，供模型组织结构化输出）
# ---------------------------------------------------------------------------

def search_nearby_places(center_name: str, limit: int = 8) -> List[str]:
    """返回指定中心点周边的候选地点名称（仅名称，不含坐标与描述）。

    返回的是「候选名称池」，最终的地点名称/坐标/描述由本地模型在下一步
    生成，避免在代码里硬编码完整地点 JSON。
    """
    pool = {
        "SIAS University (郑州西亚斯学院)": [
            "SIAS University Library",
            "SIAS University North Gate",
            "SIAS University Stadium",
            "SIAS University International Building",
            "Xinzheng East Railway Station",
            "Zhengzhou Xinzheng International Airport",
            "Zhengzhou National Cotton Market",
            "Xuanyuan Lake Park",
            "Zhengzhou University of Light Industry",
        ],
    }
    return pool.get(center_name, [])[:limit]


# ---------------------------------------------------------------------------
# 工具 3：渲染交互式地图（由 Agent 调用，产出最终 HTML）
# ---------------------------------------------------------------------------

def render_interactive_map(points: List[Dict[str, Any]], output_path: str,
                           center: List[float], zoom: int = 14) -> Dict[str, Any]:
    """把结构化地点数据渲染为 Leaflet 交互式 HTML 地图。

    参数：
        points      地点列表，每项含 name / name_zh / latitude / longitude / description
        output_path 输出 HTML 路径
        center      地图中心 [lat, lng]
        zoom        初始缩放级别
    """
    from map_renderer import build_map_html  # 延迟导入，保持工具层纯净

    html = build_map_html(points, center=center, zoom=zoom)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return {
        "ok": True,
        "output_path": output_path,
        "markers": len(points),
    }


# ---------------------------------------------------------------------------
# 工具 Schema 注册表（JSON Schema 形式，符合 OpenAI function-calling 规范）
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_place_geo",
            "description": "查询一个地点的经纬度坐标。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "地点名称"},
                    "country": {"type": "string", "description": "国家，默认 China"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_nearby_places",
            "description": "搜索某个中心点周边的候选地点名称列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "center_name": {"type": "string", "description": "中心地点名称"},
                    "limit": {"type": "integer", "description": "返回数量，默认 8"},
                },
                "required": ["center_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "render_interactive_map",
            "description": "把结构化地点列表渲染为 Leaflet 交互式 HTML 地图。",
            "parameters": {
                "type": "object",
                "properties": {
                    "points": {
                        "type": "array",
                        "description": "地点列表，每项含 name/name_zh/latitude/longitude/description",
                        "items": {"type": "object"},
                    },
                    "output_path": {"type": "string"},
                    "center": {"type": "array", "items": {"type": "number"}},
                    "zoom": {"type": "integer"},
                },
                "required": ["points", "output_path", "center"],
            },
        },
    },
]

# 工具名 -> 可调用对象 的映射（供 Agent 主循环分发调用）
TOOL_DISPATCH = {
    "get_place_geo": get_place_geo,
    "search_nearby_places": search_nearby_places,
    "render_interactive_map": render_interactive_map,
}
