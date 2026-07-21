#!/usr/bin/env python3
"""Validate generated content against repository publishing policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


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


def validate_visual_manifest(content_dir: Path) -> dict[str, object]:
    manifest_path = content_dir / "visual-source-manifest.json"
    if not manifest_path.exists():
        raise SystemExit("Publishing blocked: visual-source-manifest.json is missing.")
    payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    assets = payload.get("assets")
    if not isinstance(assets, list):
        raise SystemExit("Publishing blocked: visual-source-manifest.json has no assets list.")
    hashes = [str(asset.get("sha256", "")).strip() for asset in assets if isinstance(asset, dict)]
    unique_hashes = {value for value in hashes if value}
    minimum = int(payload.get("minimum_unique_sources") or 5)
    if len(unique_hashes) < minimum:
        raise SystemExit(
            f"Publishing blocked: visual source diversity too low "
            f"({len(unique_hashes)} unique hashes, need {minimum})."
        )
    providers = {
        str(asset.get("provider", "")).strip().lower()
        for asset in assets
        if isinstance(asset, dict)
    }
    allowed = {"pexels", "pixabay", "openai"}
    missing_provider = "" in providers
    invalid = providers - allowed - {""}
    if missing_provider or invalid:
        raise SystemExit(
            "Publishing blocked: visual-source-manifest.json must identify each asset as "
            f"one of {sorted(allowed)}; found {sorted(providers)}."
        )
    return {"engine": payload.get("engine"), "unique_visual_sources": len(unique_hashes), "visual_providers": sorted(providers)}


def validate_instagram_caption(content_dir: Path) -> dict[str, object]:
    caption_path = content_dir / "instagram-caption.txt"
    if not caption_path.exists():
        raise SystemExit("Publishing blocked: instagram-caption.txt is missing.")
    caption = caption_path.read_text(encoding="utf-8-sig")
    hashtags = re.findall(r"(?<!\w)#[A-Za-z0-9_\uac00-\ud7a3]+", caption)
    if len(hashtags) < 5:
        raise SystemExit(f"Publishing blocked: Instagram caption needs at least 5 hashtags; found {len(hashtags)}.")
    first_line = next((line.strip() for line in caption.splitlines() if line.strip()), "")
    if not first_line or not (first_line.endswith("?") or first_line.endswith("\uae4c\uc694?")):
        raise SystemExit("Publishing blocked: Instagram caption first line must be a hook question.")
    return {"instagram_hashtags": len(hashtags), "instagram_hook": first_line}


def main() -> int:
    parser = argparse.ArgumentParser(description="Block publishing for disabled content pillars.")
    parser.add_argument("--content-dir", required=True, type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args()

    disabled = load_disabled_pillars(args.policy)
    pillar = pillar_from_readme(args.content_dir) or pillar_from_publish_results(args.content_dir)
    if pillar and pillar.casefold() in disabled:
        raise SystemExit(f"Publishing blocked by content policy: pillar '{pillar}' is disabled.")
    visual = validate_visual_manifest(args.content_dir)
    instagram = validate_instagram_caption(args.content_dir)

    print(json.dumps({"status": "ok", "pillar": pillar, "disabled_pillars": sorted(disabled), **visual, **instagram}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
