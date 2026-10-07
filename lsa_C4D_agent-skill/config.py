"""C4D 本地 Agent 技能 —— 全局配置。

集中管理所有可调参数：模型、量化、Ollama 端点、推理参数等，
避免在业务代码里硬编码，方便评审者复现与二次开发。
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 本地大模型配置（评审关键信息：模型名 + 量化 + 设备）
# ---------------------------------------------------------------------------
# 本挑战在下列设备上运行（详见《lsa_C4D_方案设计.md》《lsa_C4D_验证报告.md》）：
#   设备：DESKTOP-MDK1N4L（11th Gen Intel Core i5-11300H @ 3.10GHz，4C/8T）
#   内存：16 GB（实际约 15.7 GB）
#   显卡：Intel Iris Xe 集成显卡（无独显，纯 CPU 推理）
#   系统：Windows 11（Build 26300）
# 依据 Gemma 4 家族硬件对照表，16GB 内存笔记本推荐「Gemma 4 E4B」。
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/v1/chat/completions"
OLLAMA_MODEL = "gemma4:e4b"            # 模型：Gemma 4 E4B（~4.5B effective）
MODEL_QUANT = "Q4_K_M"                  # 量化：4-bit（q4_K_M），约 4.6 GB

# 推理参数
DEFAULT_TEMPERATURE = 0.2                # 结构化输出需低温度保证确定性
DEFAULT_MAX_TOKENS = 2048
REQUEST_TIMEOUT = 600                    # 首次加载模型可能较慢，放宽超时

# ---------------------------------------------------------------------------
# 地图目标地点（核心任务：SIAS University 郑州西亚斯学院）
# ---------------------------------------------------------------------------
# 中心坐标由本地模型输出，这里仅作为「工具参数」的默认值与兜底，
# 不作为手写 JSON 的地点数据来源（地点数据一律由本地模型生成）。
CENTER_NAME = "SIAS University (郑州西亚斯学院)"
CENTER_LAT = 34.40
CENTER_LNG = 113.73
MAP_ZOOM = 14
MAP_OUTPUT = "lsa_C4D_map.html"
