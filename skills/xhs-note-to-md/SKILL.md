---
name: xhs-note-to-md
description: Convert Xiaohongshu or 小红书 notes/posts into Markdown documents by using the installed xiaohongshu-skills CLI to fetch note text, image URLs, downloaded images, optional comments, and optional image OCR. Use this skill whenever the user asks to save, archive, scrape, extract, OCR, summarize, or turn a Xiaohongshu post/link/share text into a Markdown file, especially requests like "把小红书帖子整理成 md", "只要图片 OCR 内容", "拉取评论区", "仅文字", "仅图片", or "用微信 OCR/rapidocr/paddleocr".
---

# Xiaohongshu Note To Markdown

Create a local Markdown document from a Xiaohongshu note. Use the installed `xiaohongshu-skills` project for all Xiaohongshu access, then use this skill's helper script to download images, run optional OCR, and assemble the output.

## Dependencies

Verify dependencies before starting:

- `xiaohongshu-skills`: default path `~/.codex/skills/xiaohongshu-skills`. If missing, ask the user to install `github.com/autoclaw-cc/xiaohongshu-skills` and restart Codex so the skill is discoverable.
- Browser extension bridge and Xiaohongshu login: run `python scripts/cli.py check-login` from the `xiaohongshu-skills` directory before detail extraction.
- OCR is optional. If OCR is requested and the user does not specify an engine, prefer `wx-ocr` on Windows, then `rapidocr_onnxruntime`, then `paddleocr`. See `references/dependencies.md` for install and behavior notes.

Do not use unrelated Xiaohongshu MCPs or external scrapers. The source of note data must be `xiaohongshu-skills/scripts/cli.py`.

## Mode Selection

Map the user's wording to one mode:

| User intent | Script mode | Comments |
|---|---|---|
| default / "整理成 md" / "图片和文字" | `text-images` | Fetch post text and download images. Image files are listed; add `--embed-images` only if the user wants visual image embeds. |
| "仅文字" / "只要正文" | `text-only` | No image download unless needed for another requested output. |
| "仅图片" / "只下载图片" | `images-only` | Download images and write a manifest. |
| "图片 OCR" / "只需要图片里的内容" | `ocr-only` | Download images and produce raw OCR text. Then use the LLM, not Python rules, to reconstruct the final article. |
| "正文加图片 OCR" | `text-ocr` | Include post text plus OCR text. |
| "全部" | `full` | Include metadata, post text, images, OCR if requested, and comments if requested. |

Comments are excluded by default. Add `--comments` only when the user asks for comments, comment area, 评论区, replies, or discussion.

## Workflow

1. Resolve paths:
   - `xhs_dir = ~/.codex/skills/xiaohongshu-skills`
   - `helper = <this skill>/scripts/build_xhs_note_md.py`
   - output defaults to the Desktop unless the user specifies a path.

2. Check login:
   ```powershell
   python scripts\cli.py check-login
   ```
   If it returns `logged_in: false`, follow `xiaohongshu-skills` login instructions first. Do not continue with extraction until logged in.

3. Locate the note:
   - If the user provides `feed-id` and `xsecToken`, use them directly.
   - If the user provides a full `xiaohongshu.com/explore/<id>?xsec_token=...` URL, parse `feed_id` and `xsec_token`.
   - If the user provides a short `xhslink.com` URL plus share title text, search the exact title:
     ```powershell
     python scripts\cli.py search-feeds --keyword "<title>" --sort-by 综合
     ```
     Choose the exact or closest title/user match, then use its `id` and `xsecToken`.
   - If only a short link is available and search cannot locate it, ask the user for the title, author, or a full note URL.

4. Fetch detail JSON:
   ```powershell
   python scripts\cli.py get-feed-detail --feed-id <id> --xsec-token "<token>" --keyword "<title>" > "%TEMP%\xhs_note_detail.json"
   ```
   Add `--load-all-comments` only when comments are requested and the user accepts the extra loading time.

5. Build the Markdown with this skill's script:
   ```powershell
   python "<skill_dir>\scripts\build_xhs_note_md.py" `
     --detail-json "%TEMP%\xhs_note_detail.json" `
     --output "$HOME\Desktop\<safe-title>.md" `
     --asset-dir "$HOME\Desktop\<safe-title>_images" `
     --mode text-images
   ```

6. Add options as needed:
   - OCR only:
     ```powershell
     --mode ocr-only --ocr-engine auto
     ```
     In this mode, write the helper output to a temporary raw OCR file first, then use the LLM to repair it into the final Markdown article. Do not rely on Python rules for cleanup or correction.
   - User-selected OCR:
     ```powershell
     --ocr-engine wx
     ```
     Supported values: `auto`, `wx`, `rapid`, `paddle`, `none`.
   - Include comments:
     ```powershell
     --comments
     ```
   - Embed images inside Markdown:
     ```powershell
     --embed-images
     ```
   - OCR layout is raw per image. The article reconstruction happens after the helper returns, inside the LLM response/editing step.

7. Verify the result:
   - Confirm the Markdown file exists.
   - Confirm downloaded image count equals `note.imageList` length for image modes.
   - For final `ocr-only`, confirm there are zero Markdown image references and no per-image headings. The final output should contain `## OCR 还原文章`.
   - Tell the user the output path, image count, OCR engine used, and any failed downloads/OCR items.

## Output Rules

- Preserve the post title as the top-level heading.
- Use UTF-8.
- Do not include image embeds for `ocr-only`; the user asked for content, not pictures.
- Treat `ocr-only` as a document-reconstruction task, but perform reconstruction with the LLM only. The helper script may output raw per-image OCR; the LLM should remove screenshot UI noise, repair OCR mistakes, and stitch the content into a readable article.
- Do not add Python regex/rule-based typo correction, page chrome filtering, or article stitching. If cleanup is needed, do it in the LLM repair step.
- Keep raw machine OCR segmented by image number only in the intermediate raw OCR file or when the user explicitly asks for raw OCR, per-image OCR, or debugging output.
- Mention OCR may need manual review for English names, numbers, and punctuation.

## LLM Repair Step For OCR-Only

After the helper creates raw OCR, read the raw file and use the LLM to produce the final Markdown. The LLM repair step should:

- Reconstruct one continuous article from the screenshot sequence.
- Remove repeated app chrome and status-bar artifacts such as Notes/Memo headers, `备忘录`, `通讯录`, time, battery/network labels, and repeated page UI labels.
- Correct obvious OCR mistakes using context, especially mixed Chinese/English terms, names, acronyms, and numbers.
- Preserve the author's meaning and sequence. Do not summarize, expand, or invent content.
- Use normal article paragraphs and headings where the OCR clearly implies them.
- If a passage is uncertain, keep the closest faithful reading rather than fabricating a smoother sentence.

Recommended working pattern:

1. Write raw OCR to `<output-stem>.raw-ocr.md`.
2. Read that raw file.
3. Let the LLM create final Markdown at the user-requested output path with:
   ```markdown
   # [Title]

   ## OCR 还原文章

   [LLM-repaired article]
   ```
4. Keep the raw file only if it is useful for traceability or the user asks for it.

## Helper Script

Use `scripts/build_xhs_note_md.py` instead of rewriting parsing, image downloading, and OCR glue each time. The script accepts raw CLI output even when log lines appear before or after JSON. The script intentionally does not repair OCR text; the LLM does that after reading the raw OCR output.
