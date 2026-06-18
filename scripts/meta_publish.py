#!/usr/bin/env python3
"""Publish generated carousel content to Instagram and Facebook via Meta APIs."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PublishError(RuntimeError):
    pass


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise PublishError(f"Missing required environment variable: {name}")
    return value


def graph_base() -> str:
    version = os.getenv("META_GRAPH_VERSION", "").strip() or "v25.0"
    return f"https://graph.facebook.com/{version}"


def request_json(method: str, url: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    body = urlencode(data).encode("utf-8") if data else None
    headers = {"User-Agent": "bbbb-social-automation/1.0"}
    if data:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=120) as response:
            payload = response.read()
            return json.loads(payload.decode("utf-8")) if payload else {}
    except HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        raise PublishError(f"{method} {url} failed HTTP {error.code}: {payload}") from error
    except URLError as error:
        raise PublishError(f"{method} {url} failed: {error.reason}") from error


def multipart_body(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----bbbb-social-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="{file_field}"; '
                f'filename="{file_path.name}"\r\n'
            ).encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            file_path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return b"".join(chunks), boundary


def request_multipart(url: str, fields: dict[str, str], file_field: str, file_path: Path) -> dict[str, Any]:
    body, boundary = multipart_body(fields, file_field, file_path)
    request = Request(
        url,
        data=body,
        headers={
            "User-Agent": "bbbb-social-automation/1.0",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        raise PublishError(f"POST {url} failed HTTP {error.code}: {payload}") from error


def publish_instagram_carousel(image_urls: list[str], caption: str) -> dict[str, Any]:
    account_id = require_env("INSTAGRAM_ACCOUNT_ID")
    token = require_env("META_SYSTEM_USER_ACCESS_TOKEN")
    children = []
    for image_url in image_urls:
        child = request_json(
            "POST",
            f"{graph_base()}/{account_id}/media",
            {
                "image_url": image_url,
                "is_carousel_item": "true",
                "access_token": token,
            },
        )
        children.append(child["id"])
    parent = request_json(
        "POST",
        f"{graph_base()}/{account_id}/media",
        {
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
            "access_token": token,
        },
    )
    creation_id = parent["id"]
    for _ in range(30):
        query = urlencode({"fields": "status_code,status", "access_token": token})
        status = request_json("GET", f"{graph_base()}/{creation_id}?{query}")
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") in {"ERROR", "EXPIRED"}:
            raise PublishError(f"Instagram container failed: {status}")
        time.sleep(5)
    else:
        raise PublishError("Instagram carousel container timed out.")
    result = request_json(
        "POST",
        f"{graph_base()}/{account_id}/media_publish",
        {"creation_id": creation_id, "access_token": token},
    )
    query = urlencode(
        {
            "fields": "id,permalink,timestamp,media_type",
            "access_token": token,
        }
    )
    return request_json("GET", f"{graph_base()}/{result['id']}?{query}")


def publish_facebook_multiphoto(image_paths: list[Path], caption: str) -> dict[str, Any]:
    page_id = require_env("FACEBOOK_PAGE_ID")
    token = require_env("FACEBOOK_PAGE_ACCESS_TOKEN")
    photo_ids = []
    for path in image_paths:
        photo = request_multipart(
            f"{graph_base()}/{page_id}/photos",
            {"published": "false", "access_token": token},
            "source",
            path,
        )
        photo_ids.append(photo["id"])
    attached_media = json.dumps([{"media_fbid": value} for value in photo_ids])
    post = request_json(
        "POST",
        f"{graph_base()}/{page_id}/feed",
        {
            "message": caption,
            "attached_media": attached_media,
            "access_token": token,
        },
    )
    query = urlencode(
        {
            "fields": "id,permalink_url,created_time",
            "access_token": token,
        }
    )
    info = request_json("GET", f"{graph_base()}/{post['id']}?{query}")
    info["photo_count"] = len(photo_ids)
    return info


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--carousel-dir", required=True)
    parser.add_argument("--public-base-url", required=True)
    parser.add_argument("--instagram-caption", required=True)
    parser.add_argument("--facebook-caption", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    carousel_dir = Path(args.carousel_dir)
    image_paths = sorted(carousel_dir.glob("*.png"))
    if not image_paths:
        raise PublishError(f"No PNG files found in {carousel_dir}")
    base = args.public_base_url.rstrip("/")
    image_urls = [f"{base}/{path.name}" for path in image_paths]
    payload = {
        "image_urls": image_urls,
        "instagram_caption_length": len(Path(args.instagram_caption).read_text(encoding="utf-8")),
        "facebook_caption_length": len(Path(args.facebook_caption).read_text(encoding="utf-8")),
    }
    if not args.dry_run:
        payload["instagram"] = publish_instagram_carousel(
            image_urls, Path(args.instagram_caption).read_text(encoding="utf-8").strip()
        )
        payload["facebook"] = publish_facebook_multiphoto(
            image_paths, Path(args.facebook_caption).read_text(encoding="utf-8").strip()
        )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
