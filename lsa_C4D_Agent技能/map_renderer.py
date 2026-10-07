"""C4D 本地 Agent 技能 —— Leaflet 地图渲染器。

把结构化地点数据渲染成「纯前端、可直接双击打开」的交互式 HTML 地图。
依赖 Leaflet.js + OpenStreetMap 瓦片（地图底图），标记点可点击查看详情。
支持按类别（校园/交通/文化/生活/风景）着色，提升视觉效果与可读性。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

_LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
_LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"

# 类别 -> 颜色 / 中文名（用于图例与着色）
_CATEGORY_META = {
    "campus":   {"color": "#d32f2f", "label": "校园设施"},
    "transport": {"color": "#1976d2", "label": "交通枢纽"},
    "culture":  {"color": "#7b1fa2", "label": "文化景点"},
    "living":   {"color": "#388e3c", "label": "生活配套"},
    "scenic":   {"color": "#f57c00", "label": "自然风景"},
}
_DEFAULT_COLOR = "#455a64"


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_map_html(points: List[Dict[str, Any]],
                   center: List[float], zoom: int = 14,
                   title: str = "SIAS University 周边交互式地图") -> str:
    """生成完整的 Leaflet 交互式地图 HTML 字符串。"""
    # 预处理：转义 + 补默认类别
    cats_meta = json.dumps(_CATEGORY_META, ensure_ascii=False)
    rows = []
    for p in points:
        cat = p.get("category") or "other"
        color = _CATEGORY_META.get(cat, {}).get("color", _DEFAULT_COLOR)
        rows.append({
            "name": _esc(p.get("name", "")),
            "name_zh": _esc(p.get("name_zh", p.get("name", ""))),
            "description": _esc(p.get("description", "")),
            "latitude": float(p["latitude"]),
            "longitude": float(p["longitude"]),
            "category": cat,
            "color": color,
        })
    points_json = json.dumps(rows, ensure_ascii=False)
    center_json = json.dumps(center)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{_esc(title)}</title>
<link rel="stylesheet" href="{_LEAFLET_CSS}" />
<style>
  html, body {{ margin: 0; height: 100%; font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; }}
  #map {{ position: absolute; top: 0; bottom: 0; left: 0; right: 0; }}
  .map-header {{
    position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
    z-index: 1000; background: rgba(255,255,255,0.96); padding: 9px 20px;
    border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.18);
    font-size: 15px; font-weight: 700; color: #1a3a5c;
  }}
  .map-legend {{
    position: absolute; bottom: 30px; right: 12px; z-index: 1000;
    background: rgba(255,255,255,0.95); padding: 10px 12px; border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15); font-size: 12px; color: #333; line-height: 1.7;
  }}
  .map-legend .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }}
  .map-footer {{
    position: absolute; bottom: 12px; left: 12px; z-index: 1000;
    background: rgba(255,255,255,0.9); padding: 6px 12px; border-radius: 8px;
    font-size: 12px; color: #555;
  }}
</style>
</head>
<body>
<div id="map"></div>
<div class="map-header">📍 {_esc(title)}</div>
<div class="map-legend" id="legend"></div>
<div class="map-footer">地点数据由本地 Gemma 4 模型生成 · Leaflet.js 渲染 · 可缩放/可点击标记</div>
<script src="{_LEAFLET_JS}"></script>
<script>
  const points = {points_json};
  const center = {center_json};
  const catMeta = {cats_meta};
  const map = L.map('map').setView(center, {zoom});
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);

  points.forEach(p => {{
    const popup = '<b>' + p.name_zh + '</b><br>' +
                  '<i>' + p.name + '</i><br>' +
                  '<span style="font-size:12px">' + p.description + '</span><br>' +
                  '<span style="color:#888;font-size:11px">(' + p.latitude.toFixed(4) + ', ' + p.longitude.toFixed(4) + ')</span>';
    L.circleMarker([p.latitude, p.longitude], {{
      radius: 9, color: '#fff', weight: 2, fillColor: p.color, fillOpacity: 0.9
    }}).addTo(map).bindPopup(popup).bindTooltip(p.name_zh);
  }});

  // 生成图例
  const legend = document.getElementById('legend');
  let legendHtml = '<b>图例</b><br>';
  for (const [key, meta] of Object.entries(catMeta)) {{
    legendHtml += '<span class="dot" style="background:' + meta.color + '"></span>' + meta.label + '<br>';
  }}
  legend.innerHTML = legendHtml;
</script>
</body>
</html>"""
    return html
