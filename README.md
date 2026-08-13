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
- [ ] 小红书浏览器插件桥接已配置（Chrome 加载 `extension/` 目录，见[第 5 节第 3 步](#第-3-步把插件装进-chrome)）
- [ ] 小红书账号已登录
- [ ] 如需识别图片文字，至少安装一个 OCR 引擎

推荐 OCR 安装方式：

```powershell
# Windows：优先用微信 OCR
python -m pip install wx-ocr

# 备用（Windows / macOS / Linux 通用）：RapidOCR
python -m pip install rapidocr-onnxruntime

# 备用：PaddleOCR
python -m pip install paddleocr
```

一般建议：Windows 先装 `wx-ocr`（macOS / Linux 没有 wx-ocr，直接用 `rapidocr_onnxruntime` 即可）。如果识别失败，再尝试其他引擎。

相关安装页面：

- `wx-ocr`: https://pypi.org/project/wx-ocr/
- `rapidocr-onnxruntime`: https://pypi.org/project/rapidocr-onnxruntime/
- `PaddleOCR`: https://www.paddleocr.ai/main/en/version3.x/installation.html

## 5. 安装方式（一步一步来）

本仓库捆绑了两个 skill，装一次就都有了：

- **`xhs-note-to-md`** — 小红书帖子转 Markdown（本仓库）
- **`xiaohongshu-skills`** — 小红书自动化依赖（登录 / 搜索 / 抓取，来自 [autoclaw-cc/xiaohongshu-skills](https://github.com/autoclaw-cc/xiaohongshu-skills)，MIT，见 [VENDOR-NOTICE](skills/xiaohongshu-skills/VENDOR-NOTICE.md)）

### 第 1 步：用一条 npx 命令安装 skill

1. 打开终端窗口：
   - **Windows**：按 `Win` 键，输入 `powershell`，回车；
   - **macOS**：按 `Command + 空格`，输入 `终端`（Terminal），回车。
2. 在终端里粘贴这行命令并回车：

   ```bash
   npx skills add DrErwin/xhs-note-to-md
   ```

3. 命令会进入一个选择界面，按提示操作：
   - **选择 skill**：用方向键和空格勾选 `xhs-note-to-md` 和 `xiaohongshu-skills` 两个（全选），回车确认；
   - **选择 Agent**：选你平时用的工具，比如 Codex、Claude Code、Cursor（可以多选）；
   - **选择范围**：选"全局（Global）"，这样所有项目都能用。
4. 看到"Done!"（或"Installed 2 skills"）就说明装好了。

装完后，你的 skills 目录里会多出两个文件夹（这是后面几步要用到的）：

| 系统 | skills 目录 |
|------|-------------|
| **Windows** | `C:\Users\你的用户名\.codex\skills\` |
| **macOS / Linux** | `~/.codex/skills/`（`~` 就是 `/Users/你的用户名`） |

里面应该有：

```text
xhs-note-to-md/          ← 帖子转 Markdown
xiaohongshu-skills/      ← 小红书自动化（登录/搜索/抓取）
```

> 小知识：`你的用户名` 是你的系统账户名。不确定的话，Windows 在 PowerShell 里运行 `echo $env:USERNAME`，macOS 在终端里运行 `echo $USER`。
>
> **不想用 npx？手动复制也行**：把本仓库 `skills/` 下的 `xhs-note-to-md` 和 `xiaohongshu-skills` 两个文件夹，复制到上面表格里你对应系统的 skills 目录下。

### 第 2 步：找到浏览器插件文件夹（extension）

装完 skill 后，插件文件夹**已经在你的电脑上了**，不用再去网上找。在终端里运行下面这行，会**直接帮你打开这个文件夹**：

**Windows（PowerShell）：**

```powershell
explorer "C:\Users\$env:USERNAME\.codex\skills\xiaohongshu-skills\extension"
```

**macOS（终端）：**

```bash
open ~/.codex/skills/xiaohongshu-skills/extension
```

**如果还没装 skill、想先拿到插件**，也可以直接下载（Windows / macOS 通用）：

- 方法 A：下载整个仓库压缩包 → [点这里下载 ZIP](https://github.com/DrErwin/xhs-note-to-md/archive/refs/heads/main.zip)，解压后进入 `xhs-note-to-md-main\skills\xiaohongshu-skills\extension`（macOS 解压后的路径分隔符是 `/`，即 `xhs-note-to-md-main/skills/xiaohongshu-skills/extension`）
- 方法 B：命令行 clone：`git clone https://github.com/DrErwin/xhs-note-to-md.git`，然后进入 `xhs-note-to-md/skills/xiaohongshu-skills/extension`

### 第 3 步：把插件装进 Chrome

1. 打开 Chrome 浏览器，在地址栏输入 `chrome://extensions/` 并回车。
2. 打开页面右上角的**"开发者模式"**开关。
3. 点击左上角**"加载已解压的扩展程序"**按钮。
4. 在弹出的窗口里，选择第 2 步找到的 **extension 文件夹**（注意：是选 `extension` 这一层，不是再往里）。
5. 确认列表里出现 **XHS Bridge** 这个扩展，并且它的开关是打开的。

> 装好后这个插件让 AI 能在你的浏览器里以你的身份操作小红书（用的是你真实的登录状态），全程都在你自己的浏览器里进行。

### 第 4 步：安装 Python 依赖

1. 确认电脑上有 Python 3.11 或更高版本：
   - **Windows**：没有的话去 [python.org](https://www.python.org/downloads/) 下载安装，安装时勾选 **Add python.exe to PATH**；
   - **macOS**：终端里运行 `python3 --version` 查看版本（macOS 自带 python3，或用 `brew install python` 安装新版本）。
2. 安装依赖：

   **Windows（PowerShell）：**

   ```powershell
   cd "C:\Users\$env:USERNAME\.codex\skills\xiaohongshu-skills"
   python -m pip install python-socks requests websockets
   ```

   **macOS（终端）：**

   ```bash
   cd ~/.codex/skills/xiaohongshu-skills
   python3 -m pip install --user python-socks requests websockets
   ```

   > macOS 的 pip 如果报 `externally-managed-environment` 错误，用 `brew install python` 装一个新版 Python 后重试；或者直接使用 [uv](https://docs.astral.sh/uv/)（Windows / macOS 都可用）：在 `xiaohongshu-skills` 目录里运行 `uv sync`。

### 第 5 步：登录小红书

用 Chrome 打开 [xiaohongshu.com](https://www.xiaohongshu.com) 并登录你的小红书账号。插件 + 登录状态就绪后，AI 才能帮你读取和处理帖子。

### 第 6 步：重启 Agent，验证能用

1. 重启你用的 Agent（Codex / Claude Code 等），让它重新发现刚装的 skill。
2. 在 Agent 里输入：

   ```text
   把这个小红书帖子变成文档，只要文字：
   [小红书链接或分享文案]
   ```

3. 如果提示未登录，让 Agent 执行 skill 的登录流程即可（第 5 步已登录过的话一般不会遇到）。

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
