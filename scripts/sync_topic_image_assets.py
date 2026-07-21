#!/usr/bin/env python3
"""Sync topic-matched image assets from Pexels, Pixabay, then OpenAI."""

from __future__ import annotations

import argparse
import base64
from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image

from generate_daily_content import ANCHOR_DATE, FREE_PHOTO_ROOT, active_topics


PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
PIXABAY_SEARCH_URL = "https://pixabay.com/api/"
OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"
USER_AGENT = "bbbb-autopost/1.0"

TOPIC_QUERIES: dict[str, list[str]] = {
    "mechanism-in-motion": [
        "mechanism of action medical animation",
        "skincare serum diffusion macro",
        "cosmetic science liquid flow",
        "biotech formulation process",
        "laboratory glassware motion",
    ],
    "patient-understanding-system": [
        "doctor consultation explaining screen",
        "patient education visual guide",
        "healthcare professional explaining diagram",
        "medical communication consultation",
        "clinic education material",
    ],
    "pharma-visual-proof": [
        "pharmaceutical research microscope",
        "biotechnology assay evidence",
        "clinical research data visualization",
        "scientist reviewing lab results",
        "molecular research laboratory",
    ],
    "medical-visual-production-standard": [
        "medical animation production studio",
        "scientific storyboard review",
        "healthcare video production monitor",
        "biomedical visualization workflow",
        "creative team reviewing medical content",
    ],
}

OPENAI_VISUAL_DIRECTIONS: dict[str, str] = {
    "mechanism-in-motion": (
        "Show an invisible skincare mechanism becoming visible: translucent serum streams, "
        "layered skin-barrier geometry, directional arrows implied by light, high contrast focal tension."
    ),
    "patient-understanding-system": (
        "Show a patient education journey: question marks turning into ordered visual steps, "
        "soft clinical interface panels, human-centered clarity without showing real people."
    ),
    "pharma-visual-proof": (
        "Show proof translation: abstract molecular evidence moving into a clear consumer decision path, "
        "data fragments becoming a simple visual sequence."
    ),
    "medical-visual-production-standard": (
        "Show a production review system: storyboard frames, review checkpoints, precision layers, "
        "and a disciplined visual hierarchy for medical content."
    ),
}


@dataclass(frozen=True)
class AssetCredit:
    file: str
    provider: str
    provider_id: str
    title: str
    source_url: str
    image_url: str
    creator: str
    license: str
    topic: str
    query: str
    width: int
    height: int
    sha256: str


def request_json(url: str, headers: dict[str, str] | None = None, data: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None
    request_headers = {"User-Agent": USER_AGENT, **(headers or {})}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request = Request(url, headers=request_headers, data=body)
    with urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, path: Path) -> None:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response:
        path.write_bytes(response.read())


def validate_image(path: Path) -> tuple[bool, int, int, str]:
    try:
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return width >= 700 and height >= 500, width, height, digest
    except Exception:
        return False, 0, 0, ""


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:72] or "image"


def pexels_candidates(query: str, limit: int) -> list[dict[str, str]]:
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key:
        return []
    url = f"{PEXELS_SEARCH_URL}?{urlencode({'query': query, 'orientation': 'square', 'per_page': min(limit, 80)})}"
    payload = request_json(url, headers={"Authorization": key})
    candidates = []
    for item in payload.get("photos", []):
        src = item.get("src") or {}
        image_url = src.get("large2x") or src.get("large") or src.get("original")
        if not image_url:
            continue
        candidates.append(
            {
                "provider": "pexels",
                "provider_id": str(item.get("id", "")),
                "title": item.get("alt") or query,
                "source_url": item.get("url", ""),
                "image_url": image_url,
                "creator": item.get("photographer", ""),
                "license": "Pexels License",
            }
        )
    return candidates


def pixabay_candidates(query: str, limit: int) -> list[dict[str, str]]:
    key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not key:
        return []
    params = {
        "key": key,
        "q": query,
        "image_type": "photo",
        "safesearch": "true",
        "per_page": min(limit, 200),
        "min_width": 900,
        "min_height": 700,
    }
    payload = request_json(f"{PIXABAY_SEARCH_URL}?{urlencode(params)}")
    candidates = []
    for item in payload.get("hits", []):
        image_url = item.get("largeImageURL") or item.get("webformatURL")
        if not image_url:
            continue
        candidates.append(
            {
                "provider": "pixabay",
                "provider_id": str(item.get("id", "")),
                "title": item.get("tags") or query,
                "source_url": item.get("pageURL", ""),
                "image_url": image_url,
                "creator": item.get("user", ""),
                "license": "Pixabay Content License",
            }
        )
    return candidates


def openai_asset(topic: str, query: str, index: int, topic_dir: Path) -> AssetCredit | None:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2").strip() or "gpt-image-2"
    direction = OPENAI_VISUAL_DIRECTIONS.get(topic, query)
    prompt = (
        "Create one original square Instagram carousel background for bbbb.beauty. "
        "Marketing objective: make the first slide visually hook attention in the first second "
        "while staying premium, clinical, and B2B. "
        "No logos, no readable text, no people, no product labels, no medical claims. "
        f"Topic direction: {direction} "
        f"Search context: {query}. "
        "Composition: one strong focal element, clear foreground/background depth, useful negative space "
        "for Korean headline overlay, editorial lighting, not a generic laboratory stock photo. "
        "Color system: deep navy #1E293B, pure soft beige #F8F6F2, clear aqua blue #0EA5E9."
    )
    payload = request_json(
        OPENAI_IMAGE_URL,
        headers={"Authorization": f"Bearer {key}"},
        data={"model": model, "prompt": prompt, "size": "1024x1024", "quality": "medium", "output_format": "jpeg"},
    )
    data = (payload.get("data") or [{}])[0]
    raw = data.get("b64_json")
    out = topic_dir / f"{index:02d}-openai-{slugify(query)}.jpg"
    if raw:
        out.write_bytes(base64.b64decode(raw))
    elif data.get("url"):
        download(data["url"], out)
    else:
        return None
    ok, width, height, digest = validate_image(out)
    if not ok:
        out.unlink(missing_ok=True)
        return None
    return AssetCredit(
        file=out.name,
        provider="openai",
        provider_id=model,
        title=f"Generated abstract visual: {query}",
        source_url="",
        image_url="",
        creator="OpenAI Image API",
        license="Generated asset; review before publication",
        topic=topic,
        query=query,
        width=width,
        height=height,
        sha256=digest,
    )


def sync_topic(topic: str, queries: list[str], per_topic: int, search_limit: int, min_per_topic: int) -> list[AssetCredit]:
    topic_dir = FREE_PHOTO_ROOT / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    for old_asset in [*topic_dir.glob("*.jpg"), *topic_dir.glob("*.jpeg"), *topic_dir.glob("*.png")]:
        old_asset.unlink(missing_ok=True)
    (topic_dir / "credits.json").unlink(missing_ok=True)
    credits: list[AssetCredit] = []
    seen_hashes: set[str] = set()
    seen_ids: set[tuple[str, str]] = set()

    providers = (pexels_candidates, pixabay_candidates)
    for query in queries:
        for provider in providers:
            if len(credits) >= per_topic:
                break
            try:
                candidates = provider(query, search_limit)
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
                candidates = []
            for candidate in candidates:
                if len(credits) >= per_topic:
                    break
                identity = (candidate["provider"], candidate["provider_id"])
                if identity in seen_ids:
                    continue
                seen_ids.add(identity)
                ext = Path(candidate["image_url"]).suffix.lower()
                if ext not in {".jpg", ".jpeg", ".png"}:
                    ext = ".jpg"
                out = topic_dir / f"{len(credits) + 1:02d}-{candidate['provider']}-{slugify(candidate['title'])}{ext}"
                try:
                    download(candidate["image_url"], out)
                    ok, width, height, digest = validate_image(out)
                except Exception:
                    ok, width, height, digest = False, 0, 0, ""
                if not ok or digest in seen_hashes:
                    out.unlink(missing_ok=True)
                    continue
                seen_hashes.add(digest)
                credits.append(
                    AssetCredit(
                        file=out.name,
                        provider=candidate["provider"],
                        provider_id=candidate["provider_id"],
                        title=candidate["title"],
                        source_url=candidate["source_url"],
                        image_url=candidate["image_url"],
                        creator=candidate["creator"],
                        license=candidate["license"],
                        topic=topic,
                        query=query,
                        width=width,
                        height=height,
                        sha256=digest,
                    )
                )
        if len(credits) >= per_topic:
            break

    while len(credits) < min_per_topic:
        query = queries[len(credits) % len(queries)]
        try:
            generated = openai_asset(topic, query, len(credits) + 1, topic_dir)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            generated = None
        if generated is None or generated.sha256 in seen_hashes:
            break
        seen_hashes.add(generated.sha256)
        credits.append(generated)

    (topic_dir / "credits.json").write_text(
        json.dumps([asdict(credit) for credit in credits], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return credits


def topic_for_date(target_date: date) -> str:
    topics = active_topics()
    index = (target_date - ANCHOR_DATE).days % len(topics)
    return topics[index].slug


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--topic")
    parser.add_argument("--all-topics", action="store_true")
    parser.add_argument("--per-topic", type=int, default=8)
    parser.add_argument("--search-limit", type=int, default=30)
    parser.add_argument("--min-per-topic", type=int, default=5)
    args = parser.parse_args()

    if args.all_topics:
        topics = sorted(TOPIC_QUERIES)
    else:
        topics = [args.topic or topic_for_date(date.fromisoformat(args.date))]

    summary = {}
    failures = []
    for topic in topics:
        queries = TOPIC_QUERIES.get(topic, [topic.replace("-", " ")])
        credits = sync_topic(topic, queries, args.per_topic, args.search_limit, args.min_per_topic)
        summary[topic] = {
            "count": len(credits),
            "providers": sorted({credit.provider for credit in credits}),
        }
        if len(credits) < args.min_per_topic:
            failures.append(topic)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(
            "Not enough topic-matched image assets: "
            + ", ".join(f"{topic}={summary[topic]['count']}" for topic in failures)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
