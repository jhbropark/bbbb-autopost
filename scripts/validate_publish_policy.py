#!/usr/bin/env python3
"""Validate generated content against repository publishing policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "config" / "content_policy.json"


def load_disabled_pillars(policy_path: Path) -> set[str]:
    if not policy_path.exists():
        return set()
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    return {str(value).strip().casefold() for value in payload.get("disabled_pillars", []) if str(value).strip()}


def pillar_from_readme(content_dir: Path) -> str | None:
    readme = content_dir / "README.md"
    if not readme.exists():
        return None
    for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
        normalized = line.strip()
        if normalized.lower().startswith("- pillar:"):
            return normalized.split(":", 1)[1].strip()
    return None


def pillar_from_publish_results(content_dir: Path) -> str | None:
    result_path = content_dir / "publish-results.json"
    if not result_path.exists():
        return None
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    value = payload.get("pillar")
    return str(value).strip() if value else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Block publishing for disabled content pillars.")
    parser.add_argument("--content-dir", required=True, type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args()

    disabled = load_disabled_pillars(args.policy)
    pillar = pillar_from_readme(args.content_dir) or pillar_from_publish_results(args.content_dir)
    if pillar and pillar.casefold() in disabled:
        raise SystemExit(f"Publishing blocked by content policy: pillar '{pillar}' is disabled.")

    print(json.dumps({"status": "ok", "pillar": pillar, "disabled_pillars": sorted(disabled)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
