"""Create a no-API X publishing handoff for a logged-in browser session.

This intentionally never submits a post. It prepares a reviewable local/Pages
HTML file with copy controls, a text-only compose link, and the exact image to
attach. X's web UI keeps the final publication action in the account owner's
logged-in browser session.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from urllib.parse import urlencode


def read_thread(path: Path) -> list[str]:
    return [part.strip() for part in path.read_text(encoding="utf-8").split("\n---\n") if part.strip()]


def compose_url(text: str) -> str:
    return "https://x.com/intent/post?" + urlencode({"text": text})


def post_card(number: int, text: str, image_name: str | None, is_reply: bool) -> str:
    image = ""
    if image_name:
        image = (
            '<p class="attachment">Attach this file: '
            f'<a href="{html.escape(image_name)}">{html.escape(image_name)}</a></p>'
        )
    reply_note = "Reply to the first post." if is_reply else "Start a new X post."
    return f"""
      <section class="card">
        <h2>{number:02d}</h2>
        <p class="instruction">{reply_note}</p>
        <textarea readonly>{html.escape(text)}</textarea>
        <div class="actions">
          <button data-copy="post-{number}">Copy text</button>
          <a class="compose" target="_blank" rel="noreferrer" href="{html.escape(compose_url(text), quote=True)}">Open X composer</a>
        </div>
        <pre id="post-{number}" hidden>{html.escape(text)}</pre>
        {image}
      </section>
    """


def build_html(mode: str, posts: list[str], image_name: str | None) -> str:
    cards = []
    for index, post in enumerate(posts, start=1):
        cards.append(post_card(index, post, image_name if mode == "image" and index == 1 else None, index > 1))
    mode_label = {"short": "Short text", "image": "Single image", "thread": "Thread"}[mode]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>X browser publishing handoff</title>
  <style>
    body {{ background:#0b0b0c; color:#f5f5f5; font-family:Arial,sans-serif; margin:0 auto; max-width:760px; padding:32px 20px; }}
    h1 {{ margin-bottom:4px; }} .meta {{ color:#a7a7ad; }} .card {{ border:1px solid #303036; border-radius:12px; margin:20px 0; padding:20px; }}
    h2 {{ color:#d8ff00; margin:0; }} textarea {{ box-sizing:border-box; background:#151518; border:1px solid #45454d; border-radius:8px; color:#fff; font:15px/1.5 Arial,sans-serif; height:130px; margin:12px 0; padding:12px; resize:vertical; width:100%; }}
    button,.compose {{ background:#d8ff00; border:0; border-radius:999px; color:#111; cursor:pointer; display:inline-block; font-weight:700; padding:10px 14px; text-decoration:none; }}
    .compose {{ background:#fff; margin-left:8px; }} .instruction,.attachment {{ color:#bcbcc3; }} a {{ color:#d8ff00; }}
  </style>
</head>
<body>
  <h1>X publishing handoff</h1>
  <p class="meta">Format: {mode_label}. This page uses no X API and does not submit posts automatically.</p>
  <p class="meta">Review the text, attach the specified image when present, then publish from the logged-in X browser. For a thread, publish 01 and reply with each following card.</p>
  {''.join(cards)}
  <script>
    document.querySelectorAll('[data-copy]').forEach((button) => {{
      button.addEventListener('click', async () => {{
        await navigator.clipboard.writeText(document.getElementById(button.dataset.copy).textContent);
        button.textContent = 'Copied';
        setTimeout(() => button.textContent = 'Copy text', 1200);
      }});
    }});
  </script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an X browser publishing handoff page.")
    parser.add_argument("--caption", type=Path, required=True)
    parser.add_argument("--thread", type=Path)
    parser.add_argument("--carousel-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("auto", "short", "image", "thread"), default="auto")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    mode = args.mode
    if mode == "auto":
        mode_path = args.caption.with_name("x-mode.txt")
        mode = mode_path.read_text(encoding="utf-8").strip() if mode_path.exists() else "image"
    if mode not in {"short", "image", "thread"}:
        raise SystemExit(f"Unsupported X mode: {mode}")

    caption = args.caption.read_text(encoding="utf-8").strip()
    posts = read_thread(args.thread) if mode == "thread" and args.thread else [caption]
    if mode == "thread" and not posts:
        raise SystemExit("Thread mode requires --thread with at least one post.")
    images = sorted(args.carousel_dir.glob("*.png"))
    if mode == "image" and not images:
        raise SystemExit(f"No PNG files found in {args.carousel_dir}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build_html(mode, posts, images[0].name if mode == "image" else None), encoding="utf-8")
    print(f"Created {args.out} ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
