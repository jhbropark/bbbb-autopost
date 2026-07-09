"""Ensure a local Automation ID 3 package has an X browser handoff.

This does not publish to X. It creates reviewable text files and an HTML handoff
for a logged-in browser session, then records manual-pending status in
publish-results.json when that file exists.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from x_browser_handoff import build_html, read_thread


KST = timezone(timedelta(hours=9))


def write_if_missing(path: Path, text: str) -> None:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        path.write_text(text.strip() + "\n", encoding="utf-8")


def update_publish_results(content_dir: Path, mode: str, image_name: str | None) -> None:
    result_path = content_dir / "publish-results.json"
    if not result_path.exists():
        return
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    channels = payload.setdefault("channels", {})
    channels["x"] = {
        "status": "manual_pending",
        "reason": "X API is not used for this local run; publish through the browser handoff.",
        "mode": mode,
        "post_file": "x-post.txt",
        "thread_file": "x-thread.txt",
        "handoff_file": "x-browser-handoff.html",
        "image": image_name,
        "updated_at": datetime.now(KST).isoformat(),
    }
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def append_run_report(content_dir: Path, mode: str, image_name: str | None) -> None:
    report = content_dir / "run-report.md"
    if not report.exists():
        return
    marker = "## X Manual Handoff"
    text = report.read_text(encoding="utf-8")
    if marker in text:
        return
    image_line = f"- Image attachment: `{image_name}`\n" if image_name else ""
    text += (
        "\n"
        f"{marker}\n\n"
        "- X: manual browser handoff generated.\n"
        f"- Mode: `{mode}`\n"
        "- Handoff file: `x-browser-handoff.html`\n"
        "- Post text: `x-post.txt`\n"
        "- Thread text: `x-thread.txt`\n"
        f"{image_line}"
    )
    report.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create missing X browser handoff files for a local content package.")
    parser.add_argument("--content-dir", required=True, type=Path)
    parser.add_argument("--caption", required=True)
    parser.add_argument("--mode", choices=("short", "image", "thread"), default="image")
    args = parser.parse_args()

    content_dir = args.content_dir
    if not content_dir.is_dir():
        raise SystemExit(f"Content directory not found: {content_dir}")

    image_name = "cover.png" if (content_dir / "cover.png").is_file() else None
    mode = args.mode
    if mode == "image" and not image_name:
        mode = "short"

    caption_path = content_dir / "x-post.txt"
    thread_path = content_dir / "x-thread.txt"
    mode_path = content_dir / "x-mode.txt"
    handoff_path = content_dir / "x-browser-handoff.html"

    caption = args.caption.strip()
    thread = "\n---\n".join(
        [
            caption,
            "Case note: treat the space as conditions, not only as content.",
            "Design question: what visitor behavior should the environment create?",
        ]
    )
    write_if_missing(caption_path, caption)
    write_if_missing(thread_path, thread)
    mode_path.write_text(mode + "\n", encoding="utf-8")

    posts = read_thread(thread_path) if mode == "thread" else [caption_path.read_text(encoding="utf-8").strip()]
    handoff_path.write_text(build_html(mode, posts, image_name if mode == "image" else None), encoding="utf-8")

    update_publish_results(content_dir, mode, image_name if mode == "image" else None)
    append_run_report(content_dir, mode, image_name if mode == "image" else None)

    print(
        json.dumps(
            {
                "content_dir": str(content_dir),
                "mode": mode,
                "x_post": str(caption_path),
                "x_thread": str(thread_path),
                "x_handoff": str(handoff_path),
                "image": image_name if mode == "image" else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
