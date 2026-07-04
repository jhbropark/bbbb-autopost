"""Sync free-to-use Wikimedia Commons images for social post backgrounds.

This script uses the public MediaWiki API for Wikimedia Commons. It records
license metadata next to downloaded images so generated posts can be audited.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from html import unescape
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FREE_ROOT = ROOT / "assets" / "free-image-backgrounds"
API_URL = "https://commons.wikimedia.org/w/api.php"

TOPIC_QUERIES: dict[str, list[str]] = {
    "mechanism-in-motion": ["laboratory glassware", "medical laboratory", "cosmetic laboratory"],
    "patient-understanding-system": ["doctor consultation", "patient education", "medical consultation"],
    "pharma-visual-proof": [
        "pharmaceutical laboratory",
        "biotechnology laboratory",
        "medical research laboratory",
        "laboratory microscope",
        "research laboratory",
    ],
    "medical-visual-production-standard": ["medical laboratory", "3d medical illustration", "scientific visualization"],
}

TOPIC_FILES: dict[str, list[str]] = {
    "mechanism-in-motion": [
        "File:Lab glassware.jpg",
        "File:Pipettes and Gay-Lussac burette (Alessandri 1895.3-7).png",
        "File:Microbiology stuff.jpg",
        "File:Cosmetic jar with light pink product displayed on a textured background.jpg",
    ],
    "patient-understanding-system": [
        "File:Doctor consultation.jpg",
        "File:Innovarx Global Health Pharmacists.jpg",
        "File:Korean cosmetic products.jpg",
        "File:Cosmetic jar with light pink product displayed on a textured background.jpg",
    ],
    "pharma-visual-proof": [
        "File:Microbiology stuff.jpg",
        "File:Lab glassware.jpg",
        "File:3D Medical Animation Human Wrist.jpg",
        "File:Glass building corner (Unsplash).jpg",
    ],
    "medical-visual-production-standard": [
        "File:3D Medical Animation Human Wrist.jpg",
        "File:Lab glassware.jpg",
        "File:Microbiology stuff.jpg",
        "File:Glass building corner (Unsplash).jpg",
    ],
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@dataclass(frozen=True)
class ImageCredit:
    file: str
    title: str
    description_url: str
    source_url: str
    artist: str
    license_short_name: str
    license_url: str
    usage_terms: str
    width: int
    height: int
    topic: str
    query: str


def strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value or "")
    return unescape(value).strip()


def api_get(params: dict[str, str]) -> dict[str, Any]:
    query = urlencode({"format": "json", "formatversion": "2", **params})
    request = Request(f"{API_URL}?{query}", headers={"User-Agent": "bbbb-autopost/1.0"})
    with urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def search_files(query: str, limit: int) -> list[tuple[str, dict[str, Any]]]:
    payload = api_get(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrnamespace": "6",
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url|dimensions|extmetadata",
        }
    )
    pages = payload.get("query", {}).get("pages", [])
    results = []
    for page in pages:
        title = page.get("title", "")
        infos = page.get("imageinfo", [])
        if title.startswith("File:") and infos:
            results.append((title, infos[0]))
    return results


def fetch_files(titles: list[str]) -> list[tuple[str, dict[str, Any]]]:
    payload = api_get(
        {
            "action": "query",
            "titles": "|".join(titles),
            "prop": "imageinfo",
            "iiprop": "url|dimensions|extmetadata",
        }
    )
    pages = payload.get("query", {}).get("pages", [])
    results = []
    for page in pages:
        title = page.get("title", "")
        infos = page.get("imageinfo", [])
        if title.startswith("File:") and infos:
            results.append((title, infos[0]))
    return results


def credit_from_info(topic: str, query: str, title: str, info: dict[str, Any], file_name: str) -> ImageCredit:
    meta = info.get("extmetadata", {})

    def field(name: str) -> str:
        return strip_html(meta.get(name, {}).get("value", ""))

    return ImageCredit(
        file=file_name,
        title=title,
        description_url=info.get("descriptionurl", ""),
        source_url=info.get("url", ""),
        artist=field("Artist"),
        license_short_name=field("LicenseShortName"),
        license_url=field("LicenseUrl"),
        usage_terms=field("UsageTerms"),
        width=int(info.get("width") or 0),
        height=int(info.get("height") or 0),
        topic=topic,
        query=query,
    )


def is_usable(info: dict[str, Any]) -> bool:
    url = info.get("url", "")
    ext = Path(url).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    width = int(info.get("width") or 0)
    height = int(info.get("height") or 0)
    return width >= 700 and height >= 500


def download(url: str, path: Path) -> None:
    request = Request(url, headers={"User-Agent": "bbbb-autopost/1.0"})
    with urlopen(request, timeout=120) as response:
        path.write_bytes(response.read())


def validate_image(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def sync_topic(topic: str, queries: list[str], per_topic: int, search_limit: int) -> list[ImageCredit]:
    topic_dir = FREE_ROOT / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    credits: list[ImageCredit] = []
    seen: set[str] = set()
    candidates = [("curated", title, info) for title, info in fetch_files(TOPIC_FILES.get(topic, []))]
    for query in queries:
        if len(credits) >= per_topic:
            break
        candidates.extend((query, title, info) for title, info in search_files(query, search_limit))
    for query, title, info in candidates:
        if title in seen or len(credits) >= per_topic:
            continue
        seen.add(title)
        if not info or not is_usable(info):
            continue
        ext = Path(info["url"]).suffix.lower() or ".jpg"
        file_name = f"{len(credits) + 1:02d}-{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:70]}{ext}"
        out = topic_dir / file_name
        try:
            download(info["url"], out)
            if not validate_image(out):
                out.unlink(missing_ok=True)
                continue
        except Exception:
            out.unlink(missing_ok=True)
            continue
        credits.append(credit_from_info(topic, query, title, info, file_name))
        if len(credits) >= per_topic:
            break
    (topic_dir / "credits.json").write_text(
        json.dumps([asdict(credit) for credit in credits], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return credits


def write_markdown(all_credits: dict[str, list[ImageCredit]]) -> None:
    lines = [
        "# Free Image Background Credits",
        "",
        "Images in this folder are synchronized from Wikimedia Commons using the public MediaWiki API.",
        "Each topic folder also contains `credits.json` with source URL, author, license, and dimensions.",
        "",
    ]
    for topic, credits in all_credits.items():
        lines.append(f"## {topic}")
        lines.append("")
        for credit in credits:
            lines.append(f"- `{credit.file}`")
            lines.append(f"  - Title: {credit.title}")
            lines.append(f"  - URL: {credit.description_url}")
            lines.append(f"  - Artist: {credit.artist or 'Unknown'}")
            lines.append(f"  - License: {credit.license_short_name or credit.usage_terms or 'See source'}")
            if credit.license_url:
                lines.append(f"  - License URL: {credit.license_url}")
        lines.append("")
    (FREE_ROOT / "CREDITS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-topic", type=int, default=4)
    parser.add_argument("--search-limit", type=int, default=10)
    args = parser.parse_args()

    FREE_ROOT.mkdir(parents=True, exist_ok=True)
    all_credits = {}
    for topic, queries in TOPIC_QUERIES.items():
        try:
            all_credits[topic] = sync_topic(topic, queries, args.per_topic, args.search_limit)
        except HTTPError as error:
            if error.code != 429:
                raise
            all_credits[topic] = []
    write_markdown(all_credits)
    print(json.dumps({topic: len(items) for topic, items in all_credits.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
