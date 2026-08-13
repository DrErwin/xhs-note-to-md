# Dependencies And OCR Choices

## Required Xiaohongshu dependency

Install `xiaohongshu-skills` before using this skill:

```powershell
python "C:\Users\57652\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo autoclaw-cc/xiaohongshu-skills --path . --name xiaohongshu-skills
```

Restart Codex after installing a new skill. The browser extension bridge must be configured for `xiaohongshu-skills`, and the user must be logged in.

## OCR engines

Choose OCR based on quality and setup constraints:

- `wx`: best default on Windows for Chinese Xiaohongshu long images. Install with `python -m pip install wx-ocr`. It can use bundled WeChat OCR resources and usually handles Chinese, English names, spaces, and numbers better than RapidOCR.
- `rapid`: lightweight offline fallback. Install with `python -m pip install rapidocr_onnxruntime`. It is fast and easy but may misread English names, digits, and mixed Chinese/English text.
- `paddle`: high-quality heavier fallback. Install with `python -m pip install paddleocr paddlepaddle`. Use when accuracy matters and install time is acceptable.
- `none`: skip OCR.
- `auto`: try `wx`, then `rapid`, then `paddle`.

If no OCR package is installed and the user requested OCR, ask whether to install one or proceed without OCR. Do not silently install packages when the user has not allowed environment changes.

## Common commands

OCR-only document:

```powershell
python "<skill_dir>\scripts\build_xhs_note_md.py" --detail-json "%TEMP%\xhs_note_detail.json" --output "$HOME\Desktop\note.md" --mode ocr-only --ocr-engine auto
```

`ocr-only` should be used as a raw OCR extraction step. The helper script does not repair OCR text; the agent should read the raw OCR and use the LLM to create the final `## OCR 还原文章` document. Do not add Python regex/rule-based cleanup for this repair.

Post text plus images:

```powershell
python "<skill_dir>\scripts\build_xhs_note_md.py" --detail-json "%TEMP%\xhs_note_detail.json" --output "$HOME\Desktop\note.md" --mode text-images
```

Post text plus OCR and comments:

```powershell
python "<skill_dir>\scripts\build_xhs_note_md.py" --detail-json "%TEMP%\xhs_note_detail.json" --output "$HOME\Desktop\note.md" --mode text-ocr --ocr-engine wx --comments
```
