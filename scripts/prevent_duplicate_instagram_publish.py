#!/usr/bin/env python3
"""Fail closed when the scheduled payload duplicates a recent Instagram post."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def graph_base() -> str:
    version = os.getenv("META_GRAPH_VERSION", "").strip() or "v25.0"
    return f"https://graph.facebook.com/{version}"


def normalize(value: str) -> str:
    return "\n".join(line.strip() for line in value.strip().splitlines() if line.strip())


def output_value(value: str | None) -> str:
    return " ".join((value or "").split())


def write_output(
    should_publish: bool,
    duplicate_permalink: str | None = None,
    duplicate_timestamp: str | None = None,
    check_status: str = "ok",
    error_message: str | None = None,
) -> None:
    output_path = os.getenv("GITHUB_OUTPUT", "").strip()
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as handle:
            handle.write(f"should_publish={'true' if should_publish else 'false'}\n")
            handle.write(f"duplicate_permalink={duplicate_permalink or ''}\n")
            handle.write(f"duplicate_timestamp={duplicate_timestamp or ''}\n")
            handle.write(f"check_status={check_status}\n")
            handle.write(f"error_message={output_value(error_message)}\n")


def error_text(error: Exception) -> str:
    if isinstance(error, HTTPError):
        body = error.read().decode("utf-8", errors="replace")
        return f"HTTP {error.code}: {body or error.reason}"
    return str(error)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--caption", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()

    token = os.getenv("META_SYSTEM_USER_ACCESS_TOKEN", "").strip()
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()
    if not token or not account_id:
        write_output(False)
        raise SystemExit("Instagram duplicate preflight requires Meta system token and account ID.")

    query = urlencode(
        {
            "fields": "caption,permalink,timestamp",
            "limit": str(args.limit),
            "access_token": token,
        }
    )
    request = Request(f"{graph_base()}/{account_id}/media?{query}")
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        message = error_text(error)
        write_output(True, check_status="unavailable", error_message=message)
        print(
            json.dumps(
                {
                    "should_publish": True,
                    "check_status": "unavailable",
                    "warning": "Instagram duplicate preflight failed; continuing publish so the daily run is not blocked by a read-check error.",
                    "error": message,
                },
                ensure_ascii=False,
            )
        )
        return 0

    caption = normalize(args.caption.read_text(encoding="utf-8"))
    duplicate = next(
        (
            post
            for post in payload.get("data", [])
            if normalize(post.get("caption", "")) == caption
        ),
        None,
    )
    should_publish = duplicate is None
    duplicate_permalink = duplicate.get("permalink") if duplicate else None
    duplicate_timestamp = duplicate.get("timestamp") if duplicate else None
    write_output(should_publish, duplicate_permalink, duplicate_timestamp)
    print(
        json.dumps(
            {
                "should_publish": should_publish,
                "duplicate_permalink": duplicate_permalink,
                "duplicate_timestamp": duplicate_timestamp,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
