#!/usr/bin/env python3
"""Summarize saved per-channel publish results without retrying any action."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


RESULT_FILES = {
    "instagram": "instagram-publish-results.json",
    "instagram_reel": "instagram-reel-publish-results.json",
    "facebook": "facebook-publish-results.json",
    "linkedin_ko": "linkedin-publish-results.json",
    "linkedin_en": "linkedin-english-publish-results.json",
    "x": "x-publish-results.json",
    "reddit": "reddit-publish-results.json",
}


def _failure_detail(error: object) -> str:
    """Return a safe category; do not echo provider response bodies or secrets."""
    message = error.get("message", "") if isinstance(error, dict) else str(error)
    if "missing required environment variable" in message.lower():
        return "required configuration is missing"
    match = re.search(r"\bHTTP\s+(\d{3})\b", message, re.IGNORECASE)
    if match:
        return f"HTTP {match.group(1)}; details are in the publish artifact"
    return "request failed; details are in the publish artifact"


def selected_channels(event: str, scope: str) -> list[str]:
    all_channels = ["instagram", "instagram_reel", "facebook", "linkedin_ko", "linkedin_en", "x", "reddit"]
    if event == "schedule" or scope in {"", "all"}:
        return all_channels
    return {
        "instagram": ["instagram"],
        "instagram_reel": ["instagram_reel"],
        "facebook": ["facebook"],
        "linkedin": ["linkedin_ko"],
        "linkedin_en": ["linkedin_en"],
        "x": ["x"],
        "reddit": ["reddit"],
    }.get(scope, [scope])


def summarize(
    results_dir: Path,
    expected: list[str],
    step_outcomes: dict[str, str] | None = None,
) -> tuple[list[tuple[str, str, str]], int]:
    step_outcomes = step_outcomes or {}
    rows: list[tuple[str, str, str]] = []
    failures = 0

    for channel in expected:
        filename = RESULT_FILES.get(channel)
        if filename is None:
            rows.append((channel, "FAILED", "unsupported channel identifier"))
            failures += 1
            continue

        result_path = results_dir / filename
        if not result_path.is_file():
            outcome = step_outcomes.get(channel, "")
            if outcome == "skipped":
                rows.append((channel, "SKIPPED", "workflow condition prevented an attempt"))
            else:
                detail = "publish step failed; no result receipt" if outcome == "failure" else "result file missing; no success receipt"
                rows.append((channel, "FAILED", detail))
                failures += 1
            continue

        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            rows.append((channel, "FAILED", "result file unreadable or invalid JSON"))
            failures += 1
            continue

        if not isinstance(payload, dict):
            rows.append((channel, "FAILED", "result file has unexpected structure"))
            failures += 1
            continue

        api_channel = "linkedin" if channel in {"linkedin_ko", "linkedin_en"} else channel
        errors = payload.get("errors", {})
        if isinstance(errors, dict) and api_channel in errors:
            rows.append((channel, "FAILED", _failure_detail(errors[api_channel])))
            failures += 1
            continue

        receipt = payload.get(api_channel)
        if isinstance(receipt, dict) and receipt.get("status") == "skipped":
            rows.append((channel, "SKIPPED", "workflow precondition"))
            continue
        if receipt is not None:
            if step_outcomes.get(channel) == "failure":
                rows.append((channel, "FAILED", "step failed despite a receipt; review artifact before any manual retry"))
                failures += 1
                continue
            rows.append((channel, "PUBLISHED", "success receipt present"))
            continue

        rows.append((channel, "FAILED", "result has neither an error nor a success receipt"))
        failures += 1

    return rows, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", required=True, type=Path)
    parser.add_argument("--event", required=True, help="GitHub event name")
    parser.add_argument("--scope", default="all", help="Selected publish scope")
    parser.add_argument("--step-outcomes", default="{}", help="JSON outcomes keyed by channel label")
    args = parser.parse_args()
    expected = selected_channels(args.event, args.scope)
    try:
        step_outcomes = json.loads(args.step_outcomes)
    except json.JSONDecodeError:
        step_outcomes = {}
        print("Invalid step outcome metadata; result files will still be checked.")
    if not isinstance(step_outcomes, dict):
        step_outcomes = {}
    rows, failures = summarize(args.results_dir, expected, step_outcomes)

    report = ["## Channel publish outcome", "", "No channel was retried by this summary step.", "", "| Channel | Status | Note |", "| --- | --- | --- |"]
    for channel, status, detail in rows:
        safe_detail = detail.replace("|", "\\|")
        report.append(f"| {channel} | {status} | {safe_detail} |")
    published = sum(status == "PUBLISHED" for _, status, _ in rows)
    skipped = sum(status == "SKIPPED" for _, status, _ in rows)
    report.extend(["", f"Totals: {published} published, {failures} failed, {skipped} skipped.", "Successful receipts remain in the uploaded `publish-log` artifact."])
    text = "\n".join(report) + "\n"
    print(text)
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary_file:
            summary_file.write(text)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
