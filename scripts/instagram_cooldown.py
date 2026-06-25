#!/usr/bin/env python3
"""Gate Instagram publishing while a Meta activity block is cooling down."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path


def write_output(name: str, value: str) -> None:
    output_path = os.getenv("GITHUB_OUTPUT", "").strip()
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def main() -> int:
    value = os.getenv("INSTAGRAM_COOLDOWN_UNTIL", "").strip()
    should_publish = True
    reason = ""
    if value:
        try:
            until = datetime.fromisoformat(value.replace("Z", "+00:00"))
            should_publish = datetime.now(timezone.utc) >= until.astimezone(timezone.utc)
            if not should_publish:
                reason = "instagram_activity_cooldown"
        except ValueError:
            should_publish = False
            reason = "invalid_instagram_cooldown_until"
    write_output("should_publish", "true" if should_publish else "false")
    write_output("cooldown_until", value)
    write_output("reason", reason)
    print(f"Instagram publish allowed: {should_publish}")
    if reason:
        print(f"Instagram skip reason: {reason}")
    if value:
        print(f"Instagram cooldown until: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
