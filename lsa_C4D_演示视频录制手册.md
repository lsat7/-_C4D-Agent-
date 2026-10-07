# lsa_C4D 演示视频录制手册

> 目标：录制一段 **1–2 分钟**的端到端演示视频，内容依次为 **启动 Agent → 输入一句触发工具调用的问题 → 展示地图渲染结果**。
> 本手册所有命令均可直接复制执行，无需额外摸索。
>
> 作者：lsa ｜ 日期：2026-10-07

---

## 0. 录制前的一次性准备（约 3 分钟，不录入视频）

### 0.1 确认环境就绪

```bash
# ① Ollama 是否在跑（应返回模型列表 JSON）
curl -s http://localhost:11434/api/tags

# ② 模型是否已拉取（应能看到 gemma4:e4b）
ollama list

# ③ 若未拉取，先拉（约 4.6 GB，视网速）
ollama pull gemma4:e4b

# ④ Python 依赖
cd outputs/c4d/lsa_C4D_Agent技能
pip install -r requirements.txt
```

> 若 `ollama list` 为空或没有 `gemma4:e4b`，请勿开始录制——否则视频中 Agent 会因加载模型而长时间空转，观感极差。

### 0.2 预热模型（关键，强烈建议）

首次调用需把 4.6 GB 权重从磁盘加载进内存，实测耗时 **12.3 秒**。若直接在视频里等这 12 秒，开场会显得很卡。

```bash
# 预热：发一次极短请求，把模型留在显存/内存中
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma4:e4b","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' \
  > /dev/null && echo "预热完成"
```

预热后 `keep_alive` 默认保持 5 分钟，足够录完一遍。

### 0.3 清空运行时残留文件（让视频里的输出更干净）

```bash
cd outputs/c4d/lsa_C4D_Agent技能
rm -f memory.json _model_raw_output.txt _model_locations.json _tool_call_log.json
rm -f ../lsa_C4D_map.html
```

> 删掉 `memory.json` 是为了让 Step 0 显示「0 条历史记录」，与《验证报告》的首次运行口径一致；
> 删掉旧的 `lsa_C4D_map.html` 是为了证明**视频里打开的那张地图确实是本次新生成的**。

### 0.4 布置三个窗口（录制时不再切窗口，画面更连贯）

| 窗口 | 内容 | 位置 |
|---|---|---|
| **A** | 终端（PowerShell 或 Windows Terminal），`cd` 到技能目录 | 屏幕左半 |
| **B** | 浏览器，地址栏留空（稍后输入 `file:///.../lsa_C4D_map.html`） | 屏幕右半 |
| **C** | 记事本，粘贴好「解释字幕」备查（可选） | 最小化 |

**推荐布局：终端占左 55%，浏览器占右 45%**，录屏区域直接框住这两块，避免拍到桌面图标和通知。

### 0.5 关闭干扰源

- 开启「专注助手 / 勿扰模式」，关闭微信、钉钉等弹窗
- 隐藏桌面图标（右键桌面 → 查看 → 取消勾选「显示桌面图标」）
- 浏览器按 `F11` 进入全屏，并关闭其他标签页
- 终端字号调到 **16–18 pt**（保证 1080p 下观众看得清）

---

## 1. 推荐录屏工具与关键设置

### 1.1 工具选型（Windows 为本机系统）

| 工具 | 成本 | 推荐度 | 说明 |
|---|---|---|---|
| **OBS Studio** | 免费开源 | ⭐⭐⭐⭐⭐ **首选** | 可控码率/分辨率/帧率，支持「窗口捕获 + 定时停止」，适合要控制文件体积的场景 |
| **ShareX** | 免费开源 | ⭐⭐⭐⭐ | 轻量，录屏后可直接压缩/转码，内置 FFmpeg |
| Xbox Game Bar（`Win+G`） | 系统自带 | ⭐⭐⭐ | 零安装，但码率高、体积大、不可控参数 |
| **ScreenToGif** | 免费 | ⭐⭐ | 更适合做 GIF 动图，不推荐做 mp4 演示 |

> 下文以 **OBS Studio** 为准给出参数；用 ShareX/Game Bar 的话，按下表参数在「输出设置」里靠近即可。

### 1.2 OBS 关键设置（照抄即可）

**设置 → 输出 → 输出模式改为「高级」→ 录像**

| 参数 | 推荐值 | 理由 |
|---|---|---|
| 录像格式 | **`mp4`**（或先 `mkv` 再重封装为 mp4） | 直接得到目标容器格式 |
| 视频编码器 | **`x264`（CPU 软编）** | 兼容性最好；本机无独显，NVENC 不可用 |
| 速率控制 | **CBR** | 码率可控，体积可预期 |
| 比特率 | **2500 Kbps** | 1080p 桌面演示足够清晰，且体积可控（见 §5 体积估算） |
| 预设 | **`veryfast`** | 兼顾画质与 CPU 占用（软编太慢会掉帧） |
| 关键帧间隔 | **2 秒** | 便于后期裁剪 |
| 音频编码器 | **`AAC`**，比特率 **96 Kbps** | 桌面演示人声/无音轨都够用 |

**设置 → 视频**

| 参数 | 推荐值 | 理由 |
|---|---|---|
| 基础（画布）分辨率 | **1920×1080** | 主流规格，GitHub 页面内嵌播放友好 |
| 输出（缩放）分辨率 | **1920×1080** | 不下采样，保持终端文字锐利 |
| FPS 类型 | 通用 FPS | — |
| FPS 值 | **30** | 桌面演示 30 fps 完全够用；**不要用 60**，体积会翻倍 |

**设置 → 音频**

- 若你打算**配旁白解说**：启用「麦克风/辅助音频」，并勾选「降低噪音」
- 若**不配旁白**（推荐，体积更小、无需降噪）：把「桌面音频」「麦克风」全部**静音**，只录画面

> **强烈建议：不配旁白，只录画面 + 打字。** 演示视频的核心是「看得见的 Agent 行为」，配字（在终端里 `echo` 或写在提示词里）比旁白更省体积、更适合静音观看。

### 1.3 录制区域

**来源 → 添加 → 窗口捕获 / 显示器捕获**

- 用「**显示器捕获**」+ 手动裁剪，或直接全屏录制 1920×1080，
- 保证 **终端字号 ≥ 16 pt**、**浏览器缩放 ≤ 125%**，否则观众看不清日志。

### 1.4 快捷键

| 操作 | 默认快捷键 |
|---|---|
| 开始录制 | `Ctrl + F9`（OBS 默认） |
| 停止录制 | `Ctrl + F9` |

> 若担心快捷键被其他软件占用，可在 OBS「设置 → 热键」里改成 `Ctrl + Alt + R`。

---

## 2. 分镜脚本与时间分配（总时长 1 分 40 秒）

**总控：开局 18s ｜ 输入 15s ｜ 推理等待 35s ｜ 地图 28s ｜ 收尾 4s = 100 秒**

### 环节 ①：启动 Agent（0:00 – 0:18，共 18 秒）

| 时间 | 画面动作 | 展示要点 |
|---|---|---|
| 0:00 – 0:04 | 终端窗口在前景，光标停在命令提示符 | 让观众看清当前目录是 `outputs/c4d/lsa_C4D_Agent技能` |
| 0:04 – 0:07 | 敲入并回车：`python agent.py` | — |
| 0:07 – 0:13 | 终端打印开场横幅 | **重点**：`模型：gemma4:e4b（Q4_K_M） @ http://localhost:11434` —— 一眼证明是本地模型 |
| 0:13 – 0:18 | 打印 `[Step 0] 加载记忆：0 条历史记录` | 证明跨会话记忆模块已启用 |

**该环节要拍到的原文（务必落在画面里）：**

```text
======================================================================
C4D 本地大模型 Agent 技能 —— 端到端演示
模型：gemma4:e4b（Q4_K_M） @ http://localhost:11434
======================================================================
```

> 若此处出现模型加载卡顿，直接剪掉停顿（见 §6 剪辑），保留结果帧即可。

### 环节 ②：输入一句会触发工具调用的问题（0:18 – 0:33，共 15 秒）

**关键**：`agent.py` 的 `main()` 已内置指令，**不需要你手输提示词**。为了让视频体现「输入了什么问题」，用下面任一做法：

- **做法 A（推荐，零改代码）**：在终端里先 `echo` 出要问的问题，再运行脚本：

```bash
echo "用户指令 > 给我生成一个 SIAS University 周边的地图，先搜索周边地点，再渲染成交互式地图。"
python agent.py
```

- **做法 B**：直接让脚本进入 `[Step 1]`，观众会在日志里读到这句话。

| 时间 | 画面动作 | 展示要点 |
|---|---|---|
| 0:18 – 0:24 | 终端回显这句用户指令 | **这是"输入一句会触发工具调用的问题"的证据帧，务必给足 5 秒以上停留** |
| 0:24 – 0:33 | 打印 `[Step 1] 运行 function calling 多步 Agent ...` | 让观众看到流程编号推进 |

**该指令的原文（与 `agent.py` 第 162 行完全一致）：**

```text
给我生成一个 SIAS University 周边的地图，先搜索周边地点，再渲染成交互式地图。
```

**该环节要拍到的输出：**

```text
[Step 1] 运行 function calling 多步 Agent ...
        完成，共触发 N 次工具调用，耗时 XX.Xs
        - 工具 search_nearby_places，参数 {"center_name": "SIAS University (郑州西亚斯学院)", "limit": 8}
        - 工具 get_place_geo，参数 {...}
        - 工具 render_interactive_map，参数 {...}
```

> **画面要点：必须让 `- 工具 xxx` 这几行清晰可见。** 这是「触发工具调用」的直接证据，也是评委最想看的一帧。若 `N = 1`（模型只调了一次），也如实保留，不要重录凑数。

### 环节 ③：模型推理 + 结构化输出（0:33 – 1:08，共 35 秒）

这是**纯等待段**，也是视频里唯一会「卡」的地方（本机实测约 7.69 tok/s）。

| 时间 | 画面动作 | 展示要点 |
|---|---|---|
| 0:33 – 1:02 | 终端停在 `[Step 2] 生成结构化地点数据（由本地模型生成） ...` | 可以直接**加速播放 4×–8×**，或剪掉中段；保留起始帧 + 结束帧 |
| 1:02 – 1:08 | 打印生成完毕 | **重点**：`完成，共 8 个地点，耗时 XX.Xs` + 逐条列出 8 个地点名与坐标 |

**该环节要拍到的输出：**

```text
[Step 2] 生成结构化地点数据（由本地模型生成） ...
        完成，共 8 个地点，耗时 65.7s
        - SIAS University (郑州西亚斯学院) (34.4, 113.73)
        - SIAS University Library (...)
        ...共 8 行
[Step 3] 渲染 Leaflet 交互式地图 ...
        地图已生成：lsa_C4D_map.html（标记点 8 个）
[Step 4] 已写入记忆（当前共 1 条历史记录）

✅ 全部完成。请用浏览器打开 lsa_C4D_map.html 查看交互式地图。
```

> **剪辑建议**：这一段用**变速（Time-lapse）**处理——把 35 秒的原始等待压缩到 **8–12 秒**，画面右上角叠一个「⏩ 8×」角标。这样既保留真实性，又不让观众干等。

### 环节 ④：展示地图渲染结果（1:08 – 1:36，共 28 秒）

| 时间 | 画面动作 | 展示要点 |
|---|---|---|
| 1:08 – 1:13 | 切到浏览器窗口，地址栏输入地图路径并回车 | 展示 `file:///C:/.../outputs/c4d/lsa_C4D_map.html` |
| 1:13 – 1:19 | 页面渲染出地图 | **重点**：顶部标题「📍 SIAS University 周边交互式地图」+ 8 个彩色 `circleMarker` 标记点 |
| 1:19 – 1:26 | **鼠标悬停**到标记点上 | 触发 `bindTooltip`，浮出中文地名 |
| 1:26 – 1:33 | **点击**某个标记点 | 触发 `bindPopup`，弹出「中文名 + 英文名 + 描述 + 经纬度」卡片 |
| 1:33 – 1:36 | 拖拽地图 + 滚轮缩放 | 证明是**真·交互式**地图，不是静态截图 |

**画面要点清单（逐项都要出现）：**

- ✅ 顶部标题栏：`📍 SIAS University 周边交互式地图`
- ✅ 右下角图例：校园设施（红）/ 交通枢纽（蓝）/ 文化景点（紫）/ 生活配套（绿）/ 自然风景（橙）
- ✅ 左下角脚注：`地点数据由本地 Gemma 4 模型生成 · Leaflet.js 渲染 · 可缩放/可点击标记`
- ✅ 至少 1 次悬停 tooltip + 1 次点击 popup
- ✅ 至少 1 次缩放/拖拽

> 若 OSM 瓦片加载慢（本机在沙箱环境曾出现灰底），**在 0.2 预热阶段顺便把浏览器打开一次地图页**，让瓦片进缓存；正式录制时瓦片会秒出。

### 环节 ⑤：收尾（1:36 – 1:40，共 4 秒）

回到终端，让最后一行 `✅ 全部完成。` 停在画面中央 2 秒，然后淡出。

**可选加分**：切到文件管理器，展示同目录下新生成的 `lsa_C4D_map.html`、`_model_raw_output.txt`、`_tool_call_log.json`、`memory.json` —— 证明产物真实落盘。

---

## 3. 时间分配总表（速查）

| 环节 | 起始 | 时长 | 核心画面 |
|---|---:|---:|---|
| ① 启动 Agent | 0:00 | **18s** | 模型横幅 `gemma4:e4b（Q4_K_M）` |
| ② 输入问题 | 0:18 | **15s** | 用户指令 + `- 工具 xxx` 工具调用日志 |
| ③ 模型推理 | 0:33 | **35s**（可剪成 10s） | `完成，共 8 个地点` |
| ④ 地图展示 | 1:08 | **28s** | tooltip / popup / 缩放拖拽 |
| ⑤ 收尾 | 1:36 | **4s** | `✅ 全部完成。` |
| **合计** | | **100s ≈ 1 分 40 秒** | 落在 1–2 分钟要求内 |

> 若要压缩到 1 分钟整：把环节 ③ 剪到 8 秒、环节 ① 剪到 12 秒，其余不变 → **约 67 秒**。
> 若要拉长到 2 分钟：环节 ③ 保留完整 35 秒，环节 ④ 加一段「点击第二个标记点 + 查看另一张 popup」→ **约 115 秒**。

---

## 4. 命名与体积控制

### 4.1 命名为 `lsa_C4D_demo.mp4`

录完后把文件重命名为（**大小写严格一致**）：

```bash
lsa_C4D_demo.mp4
```

- 位置：放在 `outputs/c4d/lsa_C4D_output_screenshots/` 下（与现有 7 个证据文件同目录）
- 全路径：`outputs/c4d/lsa_C4D_output_screenshots/lsa_C4D_demo.mp4`

### 4.2 目标体积：**≤ 20 MB**（建议压到 10–15 MB）

**为什么必须压：**
- GitHub **单文件硬上限 100 MB**，超过会被直接拒收；
- GitHub 对 **> 50 MB** 的文件会弹警告，且 clone 体验明显变差；
- 仓库当前总量约 1–2 MB，一个 50 MB 的视频会让仓库膨胀 20 倍以上。

**体积估算（1080p / 30fps / CBR 2500 Kbps / AAC 96 Kbps，100 秒）：**

```
视频 ≈ 2500 kbps × 100 s ÷ 8 = 31.25 MB
音频 ≈   96 kbps × 100 s ÷ 8 =  1.20 MB
合计 ≈ 32 MB  →  略偏大，需二次压缩
```

所以按下文命令压到 **目标 1200 Kbps 左右 → 约 15 MB**。

### 4.3 用 FFmpeg 压缩

**前置**：确保已安装 FFmpeg（`ffmpeg -version` 有输出即 OK；没有则 `winget install Gyan.FFmpeg`）。

```bash
# 进入视频所在目录
cd outputs/c4d/lsa_C4D_output_screenshots

# 若 OBS 录的是 mkv，先无损重封装为 mp4（秒完成，不损画质）
ffmpeg -i lsa_C4D_demo_raw.mkv -c copy lsa_C4D_demo_raw.mp4

# 一行命令完成「压缩 + 命名 + 加 faststart」
ffmpeg -i lsa_C4D_demo_raw.mp4 \
  -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p \
  -vf "scale=1920:-2" \
  -c:a aac -b:a 96k -ac 1 \
  -movflags +faststart \
  lsa_C4D_demo.mp4
```

**参数说明：**

| 参数 | 作用 |
|---|---|
| `-preset slow` | 压缩率更高、体积更小（只影响编码耗时，不影响画质） |
| `-crf 26` | 恒定质量模式，26 是「桌面录屏」的甜点值（数字越大体积越小；18 更高清但更大） |
| `-pix_fmt yuv420p` | **必须**，否则浏览器/QuickTime 可能不识别 |
| `-vf scale=1920:-2` | 锁定宽 1920、高度自动取偶数（H.264 要求偶数） |
| `-ac 1` | 转单声道，体积再省一半 |
| `-movflags +faststart` | **必须**，把索引移到文件头，GitHub 页面内嵌播放才能**边下边播** |

**若还是超过 20 MB**，逐级降档（一次改一项，看效果）：

```bash
# 方案 1：降码率（最快见效）
ffmpeg -i lsa_C4D_demo_raw.mp4 -c:v libx264 -preset slow -b:v 900k \
  -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart lsa_C4D_demo.mp4

# 方案 2：降分辨率到 720p（桌面文字仍清晰）
ffmpeg -i lsa_C4D_demo_raw.mp4 -c:v libx264 -preset slow -crf 28 \
  -vf "scale=1280:-2" -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 \
  -movflags +faststart lsa_C4D_demo.mp4

# 方案 3：纯画面、无音轨（最省体积）
ffmpeg -i lsa_C4D_demo_raw.mp4 -an -c:v libx264 -preset slow -crf 27 \
  -vf "scale=1600:-2" -pix_fmt yuv420p -movflags +faststart lsa_C4D_demo.mp4
```

### 4.4 验收压缩结果

```bash
# ① 看体积（应 ≤ 20 MB）
ls -lh lsa_C4D_demo.mp4

# ② 看时长 / 分辨率 / 编码（时长应在 60–120 秒之间）
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_name,width,height,r_frame_rate \
  -of default=noprint_wrappers=1 lsa_C4D_demo.mp4
```

**期望输出示例：**

```text
codec_name=h264
width=1920
height=1080
r_frame_rate=30/1
duration=100.20
size=15204352
```

### 4.5 清理中间产物

```bash
# 删掉原始高码率母带，只留最终版
rm -f lsa_C4D_demo_raw.mkv lsa_C4D_demo_raw.mp4
```

> 顶层 `.gitignore` 已预先忽略 `*_raw.mp4` / `*.mkv` / `*.mov`，即使忘记删也不会误入库。

---

## 5. 提交到仓库

### 5.1 目标目录

```text
lsa_C4D_output_screenshots/
```

**理由**：该目录本就是「运行证据（截图 / 日志 / 数据）」的集中存放处，已含 `00_evidence_summary.txt`、`02_map_screenshot.png`、`04_real_model_output.txt` 等。
`lsa_C4D_demo.mp4` 与它们是**同一类物证**（动态版截图），放此处与现有交付结构最一致，README 的「交付物清单」也无需新增条目。

> 备选位置：仓库根目录。**不推荐**——会打乱现有「根目录放文档 / 子目录放证据」的既有分层。

### 5.2 具体 git 命令

**方式 A：用本地 git 仓库（推荐，最快）**

```bash
cd "C:/Users/Administrator/WorkBuddy/挑战资料包/outputs/c4d"

# ① 确认视频就位且体积达标
ls -lh lsa_C4D_output_screenshots/lsa_C4D_demo.mp4

# ② 暂存
git add lsa_C4D_output_screenshots/lsa_C4D_demo.mp4

# ③ 若同时要提交本次 .gitignore 修正，一并暂存
git add .gitignore

# ④ 查看将要提交什么（确认没有误加母带）
git status --short
git diff --cached --stat

# ⑤ 提交
git commit -m "docs: 补充端到端演示视频 lsa_C4D_demo.mp4

- 内容：启动 Agent → 触发 function calling → 渲染 Leaflet 交互式地图
- 时长约 100s，1080p/30fps，H.264 + faststart，约 15MB
- 存放于 lsa_C4D_output_screenshots/，与现有截图/日志证据同目录
- 顺带修正 .gitignore 中残留的旧目录名 lsa_C4D_agent-skill"

# ⑥ 推送
git push origin main
```

**方式 B：仓库的本地工作副本已丢失时（用 GitHub API 补传）**

> 本项目历史上因沙箱限制，曾用 Git Data API 推送。若你手上没有 `outputs/c4d` 的本地 git 仓库，用仓库根目录重新拉起即可：

```bash
# 克隆到临时目录
git clone https://github.com/lsat7/-_C4D-Agent-.git /tmp/c4d-repo
cd /tmp/c4d-repo

# 拷入视频（按你的实际路径替换源）
cp "C:/Users/Administrator/WorkBuddy/挑战资料包/outputs/c4d/lsa_C4D_output_screenshots/lsa_C4D_demo.mp4" \
   lsa_C4D_output_screenshots/

git add lsa_C4D_output_screenshots/lsa_C4D_demo.mp4
git -c user.name="lsa" -c user.email="lsa@users.noreply.github.com" \
    commit -m "docs: 补充端到端演示视频 lsa_C4D_demo.mp4"
git push origin main
```

### 5.3 若视频仍 > 50 MB：考虑 Git LFS

```bash
# 安装并初始化
git lfs install
git lfs track "*.mp4"

git add .gitattributes
git commit -m "chore: 用 Git LFS 管理 mp4 大文件"

git add lsa_C4D_output_screenshots/lsa_C4D_demo.mp4
git commit -m "docs: 补充端到端演示视频 lsa_C4D_demo.mp4"
git push origin main
```

> **但首选仍是按 §4.3 压到 20 MB 以内直接提交**——GitHub 免费账户的 LFS 额度有限（1 GB 存储 / 1 GB 月流量），一个小演示视频不值得占用。

### 5.4 推送后验证

```bash
# ① 文件是否上去了（返回 JSON 含 size / download_url）
curl -s -H "Authorization: Bearer $GH_PAT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/lsat7/-_C4D-Agent-/contents/lsa_C4D_output_screenshots/lsa_C4D_demo.mp4" \
  | python -c "import sys,json; d=json.load(sys.stdin); print('size =', d.get('size'), 'bytes'); print('url  =', d.get('download_url'))"

# ② 直接打开确认能播
#    把上面打印的 download_url 粘进浏览器，应能内嵌播放（点击即可，无需下载）
```

### 5.5 在 README 中挂上视频链接（可选，但建议做）

在 `README.md` 的「真实运行证据」章节末尾追加：

```markdown
**演示视频（端到端 100 秒）**：[`lsa_C4D_output_screenshots/lsa_C4D_demo.mp4`](lsa_C4D_output_screenshots/lsa_C4D_demo.mp4)

> 依次展示：启动 Agent（本地 `gemma4:e4b` / Q4_K_M）→ 输入触发 function calling 的指令
> → 模型多步推理并生成结构化地点数据 → Leaflet 交互式地图渲染与交互。
```

---

## 6. 后期剪辑要点（提高观感，5 分钟搞定）

| 问题 | 处理 | 工具 |
|---|---|---|
| 环节 ③ 等待太久 | 变速 4×–8×，右上角叠「⏩ 8×」角标 | 剪映 / DaVinci Resolve / FFmpeg |
| 模型加载 12 秒 | 直接剪掉停顿，保留前后帧拼接 | 剪映 |
| 开场没铺垫 | 加 1 秒黑场 + 标题卡「C4D 本地大模型 Agent 技能 · lsa」 | 剪映 |
| 关键帧一晃而过 | 在「工具调用日志」「地点清单」两帧上**暂停 1.5 秒** | 剪映 |
| 想加字幕 | 只需在 5 处加：「启动 Agent」「输入指令」「模型推理」「地图渲染」「端到端完成」 | 剪映自动字幕 |

**基础 FFmpeg 变速命令（把 0:33–1:08 拉快 6 倍）：**

```bash
ffmpeg -i lsa_C4D_demo_raw.mp4 \
  -filter_complex "[0:v]trim=start=0:end=33,setpts=PTS-STARTPTS[v1]; \
                   [0:v]trim=start=33:end=68,setpts=PTS-STARTPTS,setpts=PTS/6[v2]; \
                   [0:v]trim=start=68,setpts=PTS-STARTPTS[v3]; \
                   [v1][v2][v3]concat=n=3:v=1:a=0[outv]" \
  -map "[outv]" -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p \
  -movflags +faststart lsa_C4D_demo_timelapse.mp4
```

---

## 7. 一页速查（录制当天照着做）

```text
【录前】
1) curl http://localhost:11434/api/tags           → 确认 Ollama 在跑
2) ollama list                                     → 确认有 gemma4:e4b
3) 预热模型（发一次 max_tokens=5 的短请求）
4) rm memory.json / _model_* / ../lsa_C4D_map.html
5) 终端左 55%、浏览器右 45%，字号 16–18pt，开勿扰

【OBS 设置】
1920×1080 / 30fps / mp4 / x264 / CBR 2500Kbps / veryfast / 无声或 AAC 96k

【录 100 秒】
0:00  python agent.py                    ← 拍到 gemma4:e4b（Q4_K_M）横幅
0:18  拍用户指令 + "- 工具 xxx" 日志      ← 工具调用证据帧，停留 ≥5s
0:33  [Step 2] 推理等待（后期 6× 变速）
1:08  浏览器打开 lsa_C4D_map.html         ← 悬停 tooltip + 点击 popup + 缩放
1:36  ✅ 全部完成。

【录后】
ffmpeg -i *_raw.mp4 -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p \
       -vf "scale=1920:-2" -c:a aac -b:a 96k -ac 1 -movflags +faststart \
       lsa_C4D_demo.mp4
ls -lh lsa_C4D_demo.mp4                   ← 目标 ≤ 20MB
git add lsa_C4D_output_screenshots/lsa_C4D_demo.mp4
git commit -m "docs: 补充端到端演示视频 lsa_C4D_demo.mp4"
git push origin main
```

---

## 8. 常见问题

**Q1：视频里模型输出有事实偏差（如把某地标位置标错）怎么办？**
A：**如实保留，不要重录掩盖。** 《模型输出日志》已诚实记录了 2 处事实偏差，视频是同一口径的物证。演示目的是证明「Agent 能跑通、能调工具、能渲染」，不是证明模型地理知识准确。

**Q2：工具调用只触发了 1 次，没有出现多个 `- 工具 xxx`？**
A：正常。模型可能只调 `search_nearby_places` 跳过 `get_place_geo`。**视频里如实呈现，并在字幕里说明「本次模型自主选择调用 N 个工具」**。这恰恰是 function calling「由模型自主决策」的体现，比强行凑数更有说服力。

**Q3：OSM 瓦片加载不出来，地图是灰的？**
A：先在同一浏览器打开一次地图页让瓦片入缓存；若仍不行，可在 `map_renderer.py` 里改用其他瓦片源。**不要在视频里假装地图正常**——灰底也照录，并在字幕标注原因。

**Q4：`ffmpeg` 报 `Unknown encoder 'libx264'`？**
A：装的是精简版 FFmpeg。改用 `winget install Gyan.FFmpeg` 安装完整版，或把 `-c:v libx264` 换成 `-c:v mpeg4`（兼容性差，不推荐）。

**Q5：提交时 GitHub 报 `file too large`（>100 MB）？**
A：说明压缩没生效或忘了压缩。回到 §4.3 重压；实在不行走 §5.3 的 Git LFS。

**Q6：想重新录一遍，需要注意什么？**
A：重录前**务必再次执行 §0.3 的清空步骤**（尤其删 `memory.json`），否则 Step 0 会显示「1 条历史记录」，与首次运行口径不符。
