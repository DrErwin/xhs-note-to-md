# xhs-note-to-md

[![skills.sh](https://skills.sh/b/DrErwin/xhs-note-to-md)](https://skills.sh/b/DrErwin/xhs-note-to-md)

> 一键安装：`npx skills add DrErwin/xhs-note-to-md`（交互式选择 Agent 和 skill）

## 1. 简介

`xhs-note-to-md` 用于把小红书帖子转换成 Markdown 文档。

它依赖 `xiaohongshu-skills` 获取帖子内容，也可以配合 OCR 识别图片里的文字。适合把小红书知识帖、长图笔记、截图文章整理成本地文档。

## 2. 功能特性

- 获取小红书帖子正文和图片
- OCR识别图片中的文字并将 OCR 内容还原为完整文章
- 可选抓取评论区
- 输出 Markdown 文档
- 支持指定 OCR 引擎

## 3. 使用场景

你可以在这些场景里使用：

- 看到一篇小红书干货帖，想保存成 Markdown，放进 Obsidian、Notion 或本地资料库
- 帖子正文很短，但主要内容都在图片里，想把图片里的文字整理成一篇文章
- 图片本身是备忘录、文档或长图截图，想去掉时间、电量、通讯录、备忘录标题等界面干扰，只保留正文
- 想把帖子正文和评论区一起抓下来，用于选题、调研、竞品分析或用户反馈分析
- 只想下载帖子图片，后续自己做 OCR、归档或人工整理
- 想指定 OCR 引擎，例如优先用微信 OCR 识别中文长图

## 4. 前置依赖

使用前需要准备：

- [ ] `xiaohongshu-skills` 已安装（已随本仓库捆绑，安装本 skill 时一起装即可，见[第 5 节](#5-安装方式)）
- [ ] 小红书浏览器插件桥接已配置（Chrome 加载 `extension/` 目录）
- [ ] 小红书账号已登录
- [ ] 如需识别图片文字，至少安装一个 OCR 引擎

推荐 OCR 安装方式：

```powershell
# 推荐：Windows 上优先使用
python -m pip install wx-ocr

# 备用：RapidOCR
python -m pip install rapidocr-onnxruntime

# 备用：PaddleOCR
python -m pip install paddleocr
```

一般建议先装 `wx-ocr`。如果识别失败，再尝试 `rapidocr_onnxruntime` 或 `paddleocr`。

相关安装页面：

- `wx-ocr`: https://pypi.org/project/wx-ocr/
- `rapidocr-onnxruntime`: https://pypi.org/project/rapidocr-onnxruntime/
- `PaddleOCR`: https://www.paddleocr.ai/main/en/version3.x/installation.html

## 5. 安装方式

本仓库捆绑了两个 skill，一条 `npx` 命令即可全部装上：

- **`xhs-note-to-md`** — 小红书帖子转 Markdown（本仓库）
- **`xiaohongshu-skills`** — 小红书自动化依赖（登录 / 搜索 / 抓取，来自 [autoclaw-cc/xiaohongshu-skills](https://github.com/autoclaw-cc/xiaohongshu-skills)，MIT，见 [VENDOR-NOTICE](skills/xiaohongshu-skills/VENDOR-NOTICE.md)）

### 方式一：一行 npx 安装（推荐）

本仓库已接入 [skills.sh](https://skills.sh/) 生态（`npx skills` 官方 CLI），运行：

```powershell
npx skills add DrErwin/xhs-note-to-md
```

命令会进入交互式界面，按提示选择即可，不需要记任何参数：

1. **选择 skill**：勾选上面两个 skill（全选 = 一起安装）
2. **选择 Agent**：Codex / Claude Code / Cursor / Gemini CLI 等 70+ 种，可多选
3. **选择范围**：全局（所有项目可用）或仅当前项目

想跳过交互、一次性指定全部参数也行（`-g` 全局、`-y` 跳过确认、`-a` 指定 agent、`-s` 指定 skill）：

```powershell
# 两个 skill 一起全局装进 Codex
npx skills add DrErwin/xhs-note-to-md -g -y -a codex -s xhs-note-to-md -s xiaohongshu-skills
```

### 方式二：手动复制（备选）

把仓库里 `skills/` 下的 `xhs-note-to-md` 和 `xiaohongshu-skills` 两个文件夹都复制到 agent 的 skills 目录。Codex 的 Windows 默认位置是：

```text
C:\Users\你的用户名\.codex\skills\
```

复制完成后，目录应该像这样：

```text
C:\Users\你的用户名\.codex\skills\
  xiaohongshu-skills\
    SKILL.md
    scripts\
    extension\
    skills\
  xhs-note-to-md\
    SKILL.md
    README.md
    scripts\
    references\
    agents\
```

### 第三步：装完后的配置（一次性）

skill 文件装好后，`xiaohongshu-skills` 还需要配置运行环境：

1. **安装 Python 依赖**（Python ≥ 3.11）：

   ```powershell
   cd ~\.codex\skills\xiaohongshu-skills
   python -m pip install python-socks requests websockets
   # 或者用 uv：uv sync
   ```

2. **加载 Chrome 扩展桥接**：Chrome 打开 `chrome://extensions/` → 开启开发者模式 → 点"加载已解压的扩展程序" → 选择 `~\.codex\skills\xiaohongshu-skills\extension\` 目录，确认 **XHS Bridge** 扩展已启用。

3. **登录小红书**：在 Chrome 里登录小红书，或让 agent 执行 skill 的登录流程。

4. **重启 agent**（Codex / Claude Code 等），让它重新发现已安装的 skill。

### 第四步：确认能用

在 agent 里输入：

```text
把这个小红书帖子变成文档，只要文字：
[小红书链接或分享文案]
```

如果小红书账号已登录，skill 会自动开始处理。

## 6. 快速开始

最常见用法：

```text
把这个小红书帖子变成文档，只要文字：
[小红书链接或分享文案]
```

默认行为：

- 不抓评论区
- 不嵌入图片
- 如果帖子正文完整，直接整理正文
- 如果主要内容在图片里，自动 OCR 后还原成文章

## 7. 用户交互流程

1. 用户提供小红书链接或分享文案
2. skill 检查小红书登录状态
3. 通过链接或标题定位帖子
4. 获取帖子详情
5. 判断正文是否完整
6. 根据用户要求选择处理模式
7. 生成 Markdown 文档
8. 返回保存路径

## 8. 支持的模式

| 用户说法         | 英文参数                | 行为                            |
| ---------------- | ----------------------- | ------------------------------- |
| 把帖子变成文档   | `--mode text-images`  | 整理正文，并下载图片            |
| 只要文字         | `--mode text-only`    | 只保留帖子正文                  |
| 只要图片         | `--mode images-only`  | 只下载图片                      |
| 只要图片里的内容 | `--mode ocr-only`     | 图片 OCR 后还原成文章           |
| 正文加图片内容   | `--mode text-ocr`     | 正文 + 图片 OCR                 |
| 全部都要         | `--mode full`         | 正文、图片、OCR、评论等完整输出 |
| 评论区也要       | `--comments`          | 额外抓取评论区                  |
| 嵌入图片         | `--embed-images`      | 在 Markdown 中引用图片          |
| 用微信 OCR       | `--ocr-engine wx`     | 使用微信 OCR                    |
| 用 RapidOCR      | `--ocr-engine rapid`  | 使用 RapidOCR                   |
| 用 PaddleOCR     | `--ocr-engine paddle` | 使用 PaddleOCR                  |
| 自动选择 OCR     | `--ocr-engine auto`   | 自动选择可用 OCR                |
| 不使用 OCR       | `--ocr-engine none`   | 跳过 OCR                        |

## 9. OCR 策略

默认优先使用用户指定的 OCR。

如果用户没有指定：

1. Windows 优先使用 `wx-ocr`
2. 失败时尝试 `rapidocr_onnxruntime`
3. 再失败时尝试 `paddleocr`

OCR 原始结果不会直接作为最终文章。对于长图、备忘录截图、文章截图，LLM 会继续处理：

- 删除截图界面干扰
- 修正明显 OCR 错误
- 合并断行
- 还原段落和标题
- 保留原意
- 不总结、不扩写、不编造
