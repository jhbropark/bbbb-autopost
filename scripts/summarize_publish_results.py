#!/usr/bin/env python3
"""Summarize per-channel publishing results for GitHub Actions."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


EXPECTED_FILES = {
    "instagram-publish-results.json": "Instagram carousel",
    "instagram-reel-publish-results.json": "Instagram Reel",
    "facebook-publish-results.json": "Facebook",
    "linkedin-publish-results.json": "LinkedIn Korean",
    "linkedin-english-publish-results.json": "LinkedIn English",
    "x-publish-results.json": "X",
    "reddit-publish-results.json": "Reddit",
}


def read_payload(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"errors": {"workflow": {"message": f"Could not read result: {error}"}}}


def classify(label: str, payload: dict) -> tuple[str, str]:
    errors = payload.get("errors") or {}
    if errors:
        messages = "; ".join(
            str(value.get("message", value))
            for value in errors.values()
            if isinstance(value, dict)
        ) or "Unknown publishing error"
        return "failed", messages
    key = {
        "Instagram carousel": "instagram",
        "Instagram Reel": "instagram_reel",
        "Facebook": "facebook",
        "LinkedIn Korean": "linkedin",
        "LinkedIn English": "linkedin",
        "X": "x",
        "Reddit": "reddit",
    }[label]
    if key in payload:
        return "published", ""
    return "not run", "No channel result was returned"


def build_summary(root: Path) -> tuple[str, int, int, list[str]]:
    rows: list[tuple[str, str, str]] = []
    fallback_links: list[str] = []
    for filename, label in EXPECTED_FILES.items():
        path = root / filename
        if not path.exists():
            rows.append((label, "not run", "Result file missing"))
            continue
        status, detail = classify(label, read_payload(path))
        rows.append((label, status, detail))
        if label == "X" and status == "failed":
            public_base_url = os.getenv("PUBLISH_BASE_URL", "").rstrip("/")
            if public_base_url:
                fallback_links.append(f"[{label} browser handoff]({public_base_url}/x-browser-handoff.html)")

    published = sum(status == "published" for _, status, _ in rows)
    attempted = sum(status != "not run" for _, status, _ in rows)
    failed = sum(status == "failed" for _, status, _ in rows)
    state = "PASS" if failed == 0 and attempted else "PARTIAL" if published else "FAIL"

    lines = [
        "## Channel publish summary",
        "",
        f"**{state}: {published}/{attempted} channel jobs published successfully**",
        "",
        "| Channel | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for label, status, detail in rows:
        escaped_detail = detail.replace("|", "\\|")
        lines.append(f"| {label} | {status} | {escaped_detail} |")
    if fallback_links:
        lines.extend(["", "### Manual fallback", "", *[f"- {link}" for link in fallback_links]])
    return "\n".join(lines) + "\n", published, attempted, fallback_links


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    summary, published, attempted, _ = build_summary(args.root)
    print(summary, end="")
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        Path(summary_path).open("a", encoding="utf-8").write(summary)
    print(f"channel_success={published}/{attempted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
