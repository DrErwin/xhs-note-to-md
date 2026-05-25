#!/usr/bin/env python3
"""Build a Markdown archive from xiaohongshu-skills get-feed-detail output."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Markdown from xiaohongshu-skills note detail JSON."
    )
    parser.add_argument("--detail-json", required=True, help="Raw get-feed-detail output file")
    parser.add_argument("--output", required=True, help="Markdown output path")
    parser.add_argument("--asset-dir", help="Directory for downloaded images")
    parser.add_argument(
        "--mode",
        default="text-images",
        choices=["text-images", "text-only", "images-only", "ocr-only", "text-ocr", "full"],
        help="Document content mode",
    )
    parser.add_argument(
        "--ocr-engine",
        default="none",
        choices=["none", "auto", "wx", "rapid", "paddle"],
        help="OCR engine. Use auto for wx -> rapid -> paddle.",
    )
    parser.add_argument(
        "--ocr-layout",
        default="by-image",
        choices=["by-image"],
        help="Raw OCR output layout. Repair/reconstruction is done by the LLM, not this script.",
    )
    parser.add_argument(
        "--extra-pythonpath",
        action="append",
        default=[],
        help="Extra Python module path for locally installed OCR packages",
    )
    parser.add_argument("--comments", action="store_true", help="Include comments")
    parser.add_argument("--embed-images", action="store_true", help="Embed downloaded images in Markdown")
    parser.add_argument("--source-url", help="Original share URL")
    parser.add_argument("--title", help="Override title")
    return parser.parse_args()


def read_jsonish(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    decoder = json.JSONDecoder()
    for idx, char in enumerate(raw):
        if char != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(raw[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "note" in obj:
            return obj
    raise ValueError(f"Could not find a JSON object with a 'note' key in {path}")


def clean_text(text: str | None) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\t", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def safe_filename(value: str, fallback: str = "xhs-note") -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).strip()
    value = re.sub(r"\s+", " ", value)
    return value[:80] or fallback


def timestamp_ms_to_text(value: Any) -> str:
    try:
        dt = datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
        dt = dt.astimezone(timezone(timedelta(hours=8)))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC+8")
    except Exception:
        return str(value or "")


def image_extension(url: str, content_type: str | None) -> str:
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext:
            if ext == ".jpe":
                return ".jpg"
            return ext
    lower = url.lower()
    for ext in (".webp", ".jpg", ".jpeg", ".png", ".gif", ".bmp"):
        if ext in lower:
            return ext
    return ".webp"


def download_images(note: dict[str, Any], asset_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    import requests

    asset_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    images = note.get("imageList") or []
    referer = f"https://www.xiaohongshu.com/explore/{note.get('noteId', '')}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Referer": referer,
    }
    for index, image in enumerate(images, 1):
        url = image.get("urlDefault") or image.get("url") or image.get("urlPre")
        if not url:
            failed.append({"index": index, "reason": "missing image URL"})
            continue
        candidates = [url]
        if url.startswith("http://"):
            candidates.append("https://" + url[len("http://") :])
        last_error = ""
        for candidate in candidates:
            for _ in range(3):
                try:
                    response = requests.get(candidate, headers=headers, timeout=30)
                    if response.status_code == 200 and response.content:
                        ext = image_extension(candidate, response.headers.get("content-type"))
                        path = asset_dir / f"image_{index:02d}{ext}"
                        path.write_bytes(response.content)
                        downloaded.append(
                            {
                                "index": index,
                                "path": str(path),
                                "url": candidate,
                                "bytes": len(response.content),
                            }
                        )
                        last_error = ""
                        break
                    last_error = f"status={response.status_code}, bytes={len(response.content)}"
                except Exception as exc:  # noqa: BLE001
                    last_error = repr(exc)
                time.sleep(0.4)
            if not last_error:
                break
        if last_error:
            failed.append({"index": index, "url": url, "reason": last_error})
    return downloaded, failed


def prepare_ocr_image(path: Path) -> Path:
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}:
        return path
    from PIL import Image

    target = Path(tempfile.gettempdir()) / f"{path.stem}_ocr.png"
    Image.open(path).save(target)
    return target


def ocr_with_wx(paths: list[Path]) -> list[dict[str, Any]]:
    from wx_ocr import ocr

    results = []
    for index, path in enumerate(paths, 1):
        try:
            prepared = prepare_ocr_image(path)
            lines = ocr(str(prepared), return_text_only=True)
            if isinstance(lines, str):
                lines = [line for line in lines.splitlines() if line.strip()]
            results.append({"index": index, "engine": "wx", "path": str(path), "lines": list(lines), "error": None})
        except Exception as exc:  # noqa: BLE001
            results.append({"index": index, "engine": "wx", "path": str(path), "lines": [], "error": repr(exc)})
    return results


def ocr_with_rapid(paths: list[Path]) -> list[dict[str, Any]]:
    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    results = []
    for index, path in enumerate(paths, 1):
        try:
            rows, _ = engine(str(path))
            lines = [str(row[1]).strip() for row in rows or [] if len(row) >= 2 and str(row[1]).strip()]
            results.append({"index": index, "engine": "rapid", "path": str(path), "lines": lines, "error": None})
        except Exception as exc:  # noqa: BLE001
            results.append({"index": index, "engine": "rapid", "path": str(path), "lines": [], "error": repr(exc)})
    return results


def ocr_with_paddle(paths: list[Path]) -> list[dict[str, Any]]:
    from paddleocr import PaddleOCR

    engine = PaddleOCR(use_angle_cls=True, lang="ch")
    results = []
    for index, path in enumerate(paths, 1):
        try:
            rows = engine.ocr(str(path), cls=True)
            lines: list[str] = []
            for page in rows or []:
                for row in page or []:
                    if len(row) >= 2 and isinstance(row[1], (list, tuple)):
                        text = str(row[1][0]).strip()
                        if text:
                            lines.append(text)
            results.append({"index": index, "engine": "paddle", "path": str(path), "lines": lines, "error": None})
        except Exception as exc:  # noqa: BLE001
            results.append({"index": index, "engine": "paddle", "path": str(path), "lines": [], "error": repr(exc)})
    return results


def run_ocr(paths: list[Path], requested: str) -> tuple[str, list[dict[str, Any]], list[str]]:
    if requested == "none" or not paths:
        return "none", [], []
    engines = ["wx", "rapid", "paddle"] if requested == "auto" else [requested]
    errors = []
    for engine in engines:
        try:
            if engine == "wx":
                return "wx", ocr_with_wx(paths), errors
            if engine == "rapid":
                return "rapid", ocr_with_rapid(paths), errors
            if engine == "paddle":
                return "paddle", ocr_with_paddle(paths), errors
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{engine}: {exc!r}")
    return "none", [], errors


def wants_images(mode: str) -> bool:
    return mode in {"text-images", "images-only", "ocr-only", "text-ocr", "full"}


def wants_ocr(mode: str, engine: str) -> bool:
    return mode in {"ocr-only", "text-ocr", "full"} and engine != "none"


def rel_path(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return str(path)


def build_markdown(
    data: dict[str, Any],
    output: Path,
    asset_dir: Path,
    mode: str,
    comments: bool,
    embed_images: bool,
    source_url: str | None,
    downloaded: list[dict[str, Any]],
    failed_downloads: list[dict[str, Any]],
    ocr_engine: str,
    ocr_results: list[dict[str, Any]],
    ocr_errors: list[str],
    title_override: str | None,
    ocr_layout: str,
) -> str:
    note = data["note"]
    title = title_override or note.get("title") or "小红书笔记"
    lines: list[str] = [f"# {title}", ""]
    desktop_base = output.parent

    if mode != "ocr-only":
        lines += ["## 来源信息", ""]
        if source_url:
            lines.append(f"- 原始链接：{source_url}")
        lines.append(f"- 笔记 ID：{note.get('noteId', '')}")
        user = note.get("user") or {}
        lines.append(f"- 作者：{user.get('nickname', '')}（{user.get('userId', '')}）")
        lines.append(f"- 发布时间：{timestamp_ms_to_text(note.get('time'))}")
        if note.get("ipLocation"):
            lines.append(f"- IP 属地：{note.get('ipLocation')}")
        tags = note.get("tags") or []
        if tags:
            lines.append(f"- 标签：{' '.join(tags)}")
        lines.append(f"- 图片：{len(note.get('imageList') or [])} 张，已下载 {len(downloaded)} 张")
        if ocr_engine != "none":
            lines.append(f"- OCR：{ocr_engine}")
        lines.append("")

    if mode in {"text-images", "text-only", "text-ocr", "full"}:
        body = clean_text(note.get("body") or note.get("desc"))
        lines += ["## 帖子正文", "", body or "无正文。", ""]

    if mode in {"text-images", "images-only", "full"}:
        lines += ["## 图片文件", ""]
        if downloaded:
            for item in downloaded:
                path = Path(item["path"])
                relative = rel_path(path, desktop_base)
                if embed_images:
                    lines.append(f"### 图片 {item['index']:02d}")
                    lines.append("")
                    lines.append(f"![]({relative})")
                    lines.append("")
                else:
                    lines.append(f"- 图片 {item['index']:02d}：{relative}")
        else:
            lines.append("未下载图片。")
        lines.append("")

    if mode in {"ocr-only", "text-ocr", "full"}:
        lines += ["## 图片 OCR 原始文本", ""]
        if ocr_errors:
            lines.append("OCR 引擎加载失败：")
            for error in ocr_errors:
                lines.append(f"- {error}")
            lines.append("")

        by_index = {result["index"]: result for result in ocr_results}
        indexes = [item["index"] for item in downloaded] or sorted(by_index)
        for index in indexes:
            result = by_index.get(index)
            lines.append(f"### 图片 {index:02d}")
            lines.append("")
            if not result:
                lines.append("未执行 OCR。")
            elif result.get("error"):
                lines.append(f"OCR 失败：{result['error']}")
            elif result.get("lines"):
                lines.extend(str(line).strip() for line in result["lines"] if str(line).strip())
            else:
                lines.append("未识别到文字。")
            lines.append("")

    if comments:
        lines += ["## 评论区", ""]
        note_comments = data.get("comments") or []
        if not note_comments:
            lines.append("无评论数据。")
        for comment in note_comments:
            user = (comment.get("user") or {}).get("nickname", "")
            content = clean_text(comment.get("content"))
            lines.append(f"- {user}：{content}")
            for sub in comment.get("subComments") or []:
                sub_user = (sub.get("user") or {}).get("nickname", "")
                sub_content = clean_text(sub.get("content"))
                lines.append(f"  - 回复 {sub_user}：{sub_content}")
        lines.append("")

    lines += ["## 处理日志", ""]
    lines.append(f"- 图片目录：{asset_dir}")
    lines.append(f"- 图片下载失败：{len(failed_downloads)}")
    for item in failed_downloads:
        lines.append(f"  - 图片 {item.get('index')}: {item.get('reason')}")
    if ocr_engine != "none":
        ocr_line_count = sum(len(result.get("lines") or []) for result in ocr_results)
        lines.append(f"- OCR 引擎：{ocr_engine}")
        lines.append(f"- OCR 布局：{ocr_layout}")
        lines.append(f"- OCR 行数：{ocr_line_count}")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    for item in args.extra_pythonpath:
        sys.path.insert(0, item)

    detail_path = Path(args.detail_json)
    output = Path(args.output)
    data = read_jsonish(detail_path)
    note = data["note"]
    title = args.title or note.get("title") or "小红书笔记"
    asset_dir = Path(args.asset_dir) if args.asset_dir else output.with_name(f"{safe_filename(title)}_images")

    downloaded: list[dict[str, Any]] = []
    failed_downloads: list[dict[str, Any]] = []
    if wants_images(args.mode):
        downloaded, failed_downloads = download_images(note, asset_dir)

    requested_ocr = args.ocr_engine
    if args.mode in {"ocr-only", "text-ocr", "full"} and requested_ocr == "none":
        requested_ocr = "auto"
    ocr_engine = "none"
    ocr_results: list[dict[str, Any]] = []
    ocr_errors: list[str] = []
    if wants_ocr(args.mode, requested_ocr):
        paths = [Path(item["path"]) for item in downloaded]
        ocr_engine, ocr_results, ocr_errors = run_ocr(paths, requested_ocr)

    output.parent.mkdir(parents=True, exist_ok=True)
    ocr_layout = args.ocr_layout
    markdown = build_markdown(
        data=data,
        output=output,
        asset_dir=asset_dir,
        mode=args.mode,
        comments=args.comments,
        embed_images=args.embed_images,
        source_url=args.source_url,
        downloaded=downloaded,
        failed_downloads=failed_downloads,
        ocr_engine=ocr_engine,
        ocr_results=ocr_results,
        ocr_errors=ocr_errors,
        title_override=args.title,
        ocr_layout=ocr_layout,
    )
    output.write_text(markdown, encoding="utf-8")

    report = {
        "output": str(output),
        "asset_dir": str(asset_dir),
        "mode": args.mode,
        "image_count": len(note.get("imageList") or []),
        "downloaded_count": len(downloaded),
        "failed_download_count": len(failed_downloads),
        "ocr_engine": ocr_engine,
        "ocr_layout": ocr_layout,
        "ocr_image_count": len(ocr_results),
        "ocr_line_count": sum(len(result.get("lines") or []) for result in ocr_results),
        "comments_included": bool(args.comments),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
