"""C4D 本地 Agent 技能 —— 记忆模块（Memory）。

为 Agent 提供两层记忆能力，覆盖评审维度中的「有记忆」信号：

1. 会话内记忆（short-term）：
   Agent 主循环中的 messages 列表天然构成对话上下文记忆，
   模型可基于前几轮的工具调用结果继续推理。

2. 跨会话记忆（long-term）：
   Memory 类把每次任务的「指令 → 生成的地点数据 → 使用工具」持久化到
   memory.json。下次运行时，Agent 会读取历史记录并注入 system prompt，
   从而实现「记得上次做过什么、生成过哪些地点」的能力。
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")


class Memory:
    """跨会话持久化记忆（基于 JSON 文件的轻量实现）。"""

    def __init__(self, path: str = MEMORY_FILE) -> None:
        self.path = path
        self.records: List[Dict[str, Any]] = []
        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        """从磁盘加载历史记忆；文件不存在或损坏时优雅降级为空记忆。"""
        if not os.path.exists(self.path):
            self.records = []
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.records = data.get("records", []) if isinstance(data, dict) else []
        except (json.JSONDecodeError, OSError):
            self.records = []

    def save(self) -> None:
        """把当前记忆写回磁盘。"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"records": self.records}, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    def remember(self, instruction: str, places: List[Dict[str, Any]],
                 tools_used: List[str], extra: Optional[Dict[str, Any]] = None) -> None:
        """记录一次任务执行（指令、生成的地点、用到的工具）。"""
        self.records.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "instruction": instruction,
            "num_places": len(places),
            "place_names": [p.get("name_zh") or p.get("name") for p in places],
            "tools_used": tools_used,
            "extra": extra or {},
        })
        # 只保留最近 20 条，避免无限膨胀
        self.records = self.records[-20:]
        self.save()

    # ------------------------------------------------------------------
    def recall_summary(self, max_records: int = 3) -> str:
        """把最近几条记忆压缩成一段文字，供注入 system prompt。"""
        if not self.records:
            return "（暂无历史记忆，这是首次运行。）"
        lines = [f"共 {len(self.records)} 条历史任务记录，最近 {min(max_records, len(self.records))} 条："]
        for r in self.records[-max_records:]:
            names = "、".join(r.get("place_names", [])[:5])
            lines.append(
                f"- [{r['timestamp']}] 指令：{r['instruction']}；"
                f"生成 {r['num_places']} 个地点（{names}）；使用工具：{','.join(r.get('tools_used', []))}"
            )
        return "\n".join(lines)

    def known_places(self) -> List[str]:
        """返回历史上生成过的所有地点名（去重）。"""
        seen: List[str] = []
        for r in self.records:
            for n in r.get("place_names", []):
                if n and n not in seen:
                    seen.append(n)
        return seen
