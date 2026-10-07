# lsa_C4D_教学说明

> 挑战：C4D 本地大模型 Agent 技能 ｜ 作者：lsa
> 目标：任何人照着本文，都能在自己的 Windows / macOS / Linux 电脑上
> 从零复现「本地 Gemma 4 Agent 生成 SIAS 周边交互式地图」全流程。
> 全程预计 **30 分钟内**（含模型下载，视网速而定）。

---

## 0. 你需要准备什么

| 硬件/软件 | 最低要求 | 说明 |
|---|---|---|
| 内存 | ≥ 8 GB（推荐 16 GB） | E2B 需 ~5GB，E4B 需 ~5GB |
| 磁盘 | ≥ 10 GB 可用 | 模型权重 4–5 GB + 运行时 ~1.5 GB |
| 系统 | Windows 10/11、macOS、Linux 均可 | 本教程以 Windows 11 实测为例 |
| 网络 | 能访问 ollama.com | 模型下载需要；运行推理时**无需联网** |
| Python | ≥ 3.9 | 仅需一个第三方库 `requests` |

---

## 1. 第一步：安装 Ollama（约 3 分钟）

### Windows
1. 打开 <https://ollama.com/download>，下载 `OllamaSetup.exe`；
2. 双击安装（默认即可），安装完成后 Ollama 会自动在后台运行；
3. 验证：打开终端（PowerShell 或 CMD）执行

```powershell
ollama --version
# 输出示例：ollama version is 0.40.0
```

### macOS / Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

> 💡 若 `ollama --version` 报“不是内部或外部命令”，请重启终端
> （Windows 安装器会把 Ollama 加入 PATH，重启终端后生效）。

---

## 2. 第二步：下载 Gemma 4 模型（约 5–20 分钟，视网速）

按你的设备选择（16GB 内存笔记本选 E4B）：

| 你的设备 | 执行命令 |
|---|---|
| 8GB 内存笔记本 / 老电脑 | `ollama pull gemma4:e2b` |
| **16GB 内存笔记本（本方案选定）** | **`ollama pull gemma4:e4b`** |
| 16GB+ 显存 GPU | `ollama pull gemma4:26b` |
| 24GB+ 显存 GPU / 32GB+ Mac | `ollama pull gemma4:31b` |

```powershell
ollama pull gemma4:e4b
# pulling manifest ... 成功后执行下面这行验证
ollama list
# 应看到：gemma4:e4b    ...    约 4.6 GB
```

查看模型确切量化信息（评审要求的“模型+量化”标注依据）：

```powershell
ollama show gemma4:e4b
# 关注 Model → quantization 字段（如 Q4_K_M）
```

---

## 3. 第三步：先把模型当聊天伙伴跑通（Level 1，约 2 分钟）

```powershell
ollama run gemma4:e4b
>>> 请用一段话介绍郑州西亚斯学院（SIAS University）
```

模型会输出一段介绍文字——**这就是 Level 1 的“基本对话”证明**，
此时可截图（需包含模型名、你的设备信息）。
输入 `/bye` 退出。

再验证 OpenAI 兼容 API 可用（Agent 代码走的就是这个接口）：

```powershell
curl http://localhost:11434/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"gemma4:e4b\",\"messages\":[{\"role\":\"user\",\"content\":\"你好，请回复：本地模型运行正常\"}]}"
```

返回 JSON 且 `choices[0].message.content` 有内容即成功。

---

## 4. 第四步：运行本技能包（Level 2–3，约 3 分钟）

### 4.1 安装依赖

```bash
cd lsa_C4D_agent-skill
pip install -r requirements.txt     # 只有 requests 一个依赖
```

### 4.2 一键运行端到端流水线

```bash
python agent.py
```

> 💡 想一步到位（拉模型 + 跑 Agent + 采 tok/s + 出证据清单），用打包好的
> 一键脚本：`python ../finalize_evidence.py`（从 `lsa_C4D_agent-skill` 目录运行），
> 它会自动完成第四、五、七步并采集评审要求的推理速度证据。

预期输出（节选）：

```
======================================================================
C4D 本地大模型 Agent 技能 —— 端到端演示
模型：gemma4:e4b（Q4_K_M） @ http://localhost:11434
======================================================================

[Step 0] 加载记忆：N 条历史记录
[Step 1] 运行 function calling 多步 Agent ...
        - 工具 get_place_geo，参数 {"name": "SIAS University"}
        - 工具 search_nearby_places，参数 {...}
[Step 2] 生成结构化地点数据（由本地模型生成） ...
        - 郑州西亚斯学院 (34.4005, 113.7302)
        ...
[Step 3] 渲染 Leaflet 交互式地图 ...
        地图已生成：lsa_C4D_map.html（标记点 8 个）
[Step 4] 已写入记忆（当前共 N+1 条历史记录）

✅ 全部完成。请用浏览器打开 lsa_C4D_map.html 查看交互式地图。
```

### 4.3 查看地图

双击生成的 `lsa_C4D_map.html`（或把它拖进浏览器）：

- 滚轮缩放 / 拖动平移；
- 点击彩色圆点 → 弹出中英文名、描述、精确坐标；
- 右下角图例：🔴 校园设施 🔵 交通枢纽 🟣 文化景点 🟢 生活配套 🟠 自然风景。

**到这里，Level 1（跑通模型）+ Level 2（Agent 函数调用 + 交互式地图）已完成。**

---

## 5. 第五步：体验 Agent 的“记忆”（Level 3 加分演示）

```bash
python agent.py     # 第二次运行
```

注意 `[Step 0] 加载记忆：1 条历史记录`——Agent 记得你上一次生成过哪些地点，
并把记忆注入了 system prompt（见 `agent.py:run_tool_calling_agent` 中的
`mem.recall_summary()`）。这体现的是**跨会话记忆**，也是评审维度中“有记忆”的依据。

删除 `memory.json` 即可重置记忆。

---

## 6. 常见问题（FAQ / 排错）

| 现象 | 原因 | 解决 |
|---|---|---|
| `Connection refused localhost:11434` | Ollama 服务没启动 | 打开 Ollama 应用，或运行 `ollama serve` |
| `model 'gemma4:e4b' not found` | 模型没下载 | 重新执行 `ollama pull gemma4:e4b` |
| 首次请求很慢才出字 | 模型冷加载进内存 | 属正常现象，第二次起明显变快 |
| 推理速度慢（<5 tok/s） | 纯 CPU 推理 | 换 `gemma4:e2b`，或关掉大程序释放内存 |
| 地图打开是灰色无标记 | 浏览器拦截了 file:// 下的 CDN | 允许加载脚本，或用本地静态服务器：`python -m http.server` 后访问 localhost:8000 |
| 地图底图瓦片不显示 | 无网络访问 OSM | 底图需联网；离线方案见 §7 |
| JSON 解析报错 | 个别小模型输出带代码块围栏 | `agent.py` 已内置围栏清理；仍报错可换 e4b 及以上 |

---

## 7. 进阶玩法（对应 Level 3/4）

1. **离线地图底图**：把 OSM 瓦片缓存到本地或换用本地 XYZ 瓦片服务，
   修改 `map_renderer.py` 中 `tileLayer` 的 URL 即可。
2. **换模型对比**（Level 4 量化对比）：分别 `pull gemma4:e2b` / `e4b`，
   改 `config.py` 的 `OLLAMA_MODEL` 各跑一轮，用 `ollama ps` 与任务管理器
   记录内存占用、响应时间，即可得到 Q4 量化下 E2B vs E4B 的对比数据。
3. **测量真实 tok/s**（补全验证报告 V7）：

   ```powershell
   ollama run gemma4:e4b --verbose
   >>> List 8 landmarks near SIAS University in JSON
   # 输出末尾会打印 eval rate（tokens/s）——截图即为评审要求的推理速度证据
   ```

4. **多语言地图**：把 `agent.py` 中 `STRUCTURED_PROMPT` 的要求改为
   “description 字段输出中英双语”，重新运行即可。

---

## 8. 复现核对清单（打勾即完成）

- [ ] Ollama 安装成功（`ollama --version` 有输出）
- [ ] `ollama pull gemma4:e4b` 完成（`ollama list` 可见）
- [ ] `ollama run` 能对话并介绍西亚斯学院（Level 1 ✅）
- [ ] `pip install -r requirements.txt` 成功
- [ ] `python agent.py` 跑通，无报错
- [ ] 浏览器打开 `lsa_C4D_map.html`，8 个标记可点击（Level 2 ✅）
- [ ] 第二次运行 `python agent.py` 提示“加载记忆：1 条”（Level 3 记忆 ✅）
- [ ] `--verbose` 记录 tok/s 并截图（补充验证报告 V7）
