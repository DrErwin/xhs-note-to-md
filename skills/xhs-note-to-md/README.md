# xhs-note-to-md

## 1. 简介

`xhs-note-to-md` 用于把小红书帖子转换成 Markdown 文档。

它依赖 `xiaohongshu-skills` 获取帖子内容，也可以配合 OCR 识别图片里的文字。适合把小红书知识帖、长图笔记、截图文章整理成本地文档。

## 2. 功能特性

- 获取小红书帖子正文
- 下载帖子图片
- 识别图片中的文字
- 将 OCR 内容还原为完整文章
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

- 已安装 `xiaohongshu-skills`
- 小红书浏览器插件桥接已配置
- 小红书账号已登录
- 如需识别图片文字，至少安装一个 OCR 引擎

推荐 OCR 安装方式：

```powershell
# 推荐：Windows 上优先使用
python -m pip install wx-ocr

# 备用：RapidOCR
python -m pip install rapidocr-onnxruntime

# 备用：PaddleOCR
python -m pip install paddleocr
```

如果普通安装遇到权限问题，可以尝试：

```powershell
python -m pip install --user wx-ocr
```

一般建议先装 `wx-ocr`。如果识别失败，再尝试 `rapidocr_onnxruntime` 或 `paddleocr`。

相关安装页面：

- `wx-ocr`: https://pypi.org/project/wx-ocr/
- `rapidocr-onnxruntime`: https://pypi.org/project/rapidocr-onnxruntime/
- `PaddleOCR`: https://www.paddleocr.ai/main/en/version3.x/installation.html

## 5. 安装方式（一步一步来）

本仓库捆绑了两个 skill，装一次就都有了：`xhs-note-to-md`（本 skill）和 `xiaohongshu-skills`（小红书自动化依赖）。

### 第 1 步：用一条 npx 命令安装 skill

1. 按 `Win` 键，输入 `powershell`，回车，打开 PowerShell。
2. 粘贴下面这行并回车：

   ```powershell
   npx skills add DrErwin/xhs-note-to-md
   ```

3. 在交互界面里：**勾选两个 skill** → **选择你的 Agent**（Codex / Claude Code / Cursor 等）→ **选择"全局"**。
4. 看到 "Done!" 就装好了。你的电脑上会多出：

   ```text
   C:\Users\你的用户名\.codex\skills\
     xhs-note-to-md\          ← 帖子转 Markdown
     xiaohongshu-skills\      ← 小红书自动化（登录/搜索/抓取）
   ```

> 不确定 `你的用户名` 是什么？PowerShell 里运行 `echo $env:USERNAME` 就能看到。
>
> 不用 npx 的话，也可以把仓库 `skills/` 下的两个文件夹手动复制到上面的目录。

### 第 2 步：找到浏览器插件文件夹（extension）

插件文件夹**已经在你的电脑上了**，不用去网上找。在 PowerShell 里运行下面这行，会直接帮你打开它：

```powershell
explorer "C:\Users\$env:USERNAME\.codex\skills\xiaohongshu-skills\extension"
```

还没装 skill、想先拿插件？直接下载整个仓库压缩包：[点这里下载 ZIP](https://github.com/DrErwin/xhs-note-to-md/archive/refs/heads/main.zip)，解压后进入 `xhs-note-to-md-main\skills\xiaohongshu-skills\extension`。

### 第 3 步：把插件装进 Chrome

1. Chrome 地址栏输入 `chrome://extensions/` 回车。
2. 打开右上角**"开发者模式"**。
3. 点**"加载已解压的扩展程序"**，选择第 2 步的 **extension 文件夹**。
4. 确认列表里出现 **XHS Bridge** 且开关已打开。

### 第 4 步：安装 Python 依赖

```powershell
cd "C:\Users\$env:USERNAME\.codex\skills\xiaohongshu-skills"
python -m pip install python-socks requests websockets
```

（需要 Python ≥ 3.11；用 [uv](https://docs.astral.sh/uv/) 的话运行 `uv sync` 也行。）

### 第 5 步：登录小红书

用 Chrome 打开 [xiaohongshu.com](https://www.xiaohongshu.com) 并登录你的小红书账号。

### 第 6 步：重启 Agent，验证能用

1. 重启你的 Agent（Codex / Claude Code 等）。
2. 输入：

   ```text
   把这个小红书帖子变成文档，只要文字：
   [小红书链接或分享文案]
   ```

3. 如果提示未登录，让 Agent 执行 skill 的登录流程即可。

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

| 用户说法 | 英文参数 | 行为 |
|---|---|---|
| 把帖子变成文档 | `--mode text-images` | 整理正文，并下载图片 |
| 只要文字 | `--mode text-only` | 只保留帖子正文 |
| 只要图片 | `--mode images-only` | 只下载图片 |
| 只要图片里的内容 | `--mode ocr-only` | 图片 OCR 后还原成文章 |
| 正文加图片内容 | `--mode text-ocr` | 正文 + 图片 OCR |
| 全部都要 | `--mode full` | 正文、图片、OCR、评论等完整输出 |
| 评论区也要 | `--comments` | 额外抓取评论区 |
| 嵌入图片 | `--embed-images` | 在 Markdown 中引用图片 |
| 用微信 OCR | `--ocr-engine wx` | 使用微信 OCR |
| 用 RapidOCR | `--ocr-engine rapid` | 使用 RapidOCR |
| 用 PaddleOCR | `--ocr-engine paddle` | 使用 PaddleOCR |
| 自动选择 OCR | `--ocr-engine auto` | 自动选择可用 OCR |
| 不使用 OCR | `--ocr-engine none` | 跳过 OCR |

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
