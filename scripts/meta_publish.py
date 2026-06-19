#!/usr/bin/env python3
"""Publish generated carousel content to Instagram, Facebook, LinkedIn, and X."""

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


def request_json_with_headers(
    method: str,
    url: str,
    headers: dict[str, str],
    data: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=120) as response:
            payload = response.read()
            parsed = json.loads(payload.decode("utf-8")) if payload else {}
            return parsed, dict(response.headers.items())
    except HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        raise PublishError(f"{method} {url} failed HTTP {error.code}: {payload}") from error
    except URLError as error:
        raise PublishError(f"{method} {url} failed: {error.reason}") from error


def request_bytes(method: str, url: str, body: bytes, headers: dict[str, str]) -> None:
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=120):
            return
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


def linkedin_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {require_env('LINKEDIN_ACCESS_TOKEN')}",
        "Linkedin-Version": os.getenv("LINKEDIN_VERSION", "202605"),
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "User-Agent": "bbbb-social-automation/1.0",
    }


def upload_linkedin_image(image_path: Path, owner: str) -> str:
    initialized, _ = request_json_with_headers(
        "POST",
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        linkedin_headers(),
        {"initializeUploadRequest": {"owner": owner}},
    )
    value = initialized.get("value", {})
    upload_url = value.get("uploadUrl")
    image_urn = value.get("image")
    if not upload_url or not image_urn:
        raise PublishError(f"LinkedIn image initialization failed: {initialized}")

    request_bytes(
        "PUT",
        upload_url,
        image_path.read_bytes(),
        {
            "Authorization": f"Bearer {require_env('LINKEDIN_ACCESS_TOKEN')}",
            "Content-Type": mimetypes.guess_type(image_path.name)[0] or "application/octet-stream",
            "User-Agent": "bbbb-social-automation/1.0",
        },
    )
    return image_urn


def publish_linkedin_post(image_path: Path, caption: str) -> dict[str, Any]:
    author = require_env("LINKEDIN_AUTHOR_URN")
    image_urn = upload_linkedin_image(image_path, author)
    payload = {
        "author": author,
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {"media": {"id": image_urn, "title": image_path.stem}},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    response, headers = request_json_with_headers(
        "POST",
        "https://api.linkedin.com/rest/posts",
        linkedin_headers(),
        payload,
    )
    post_id = next((value for key, value in headers.items() if key.lower() == "x-restli-id"), None)
    return {"id": post_id, "response": response, "image": image_urn}


def x_headers(content_type: str = "application/json") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {require_env('X_ACCESS_TOKEN')}",
        "Content-Type": content_type,
        "User-Agent": "bbbb-social-automation/1.0",
    }


def upload_x_image(image_path: Path) -> str:
    body, boundary = multipart_body(
        {
            "media_category": "tweet_image",
            "media_type": mimetypes.guess_type(image_path.name)[0] or "application/octet-stream",
        },
        "media",
        image_path,
    )
    request = Request(
        "https://api.x.com/2/media/upload",
        data=body,
        headers=x_headers(f"multipart/form-data; boundary={boundary}"),
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as result:
            payload = result.read()
            response = json.loads(payload.decode("utf-8")) if payload else {}
    except HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        raise PublishError(f"POST https://api.x.com/2/media/upload failed HTTP {error.code}: {payload}") from error
    except URLError as error:
        raise PublishError(f"POST https://api.x.com/2/media/upload failed: {error.reason}") from error
    data = response.get("data", {})
    media_id = data.get("id") or data.get("media_id_string")
    if not media_id:
        raise PublishError(f"X media upload did not return an ID: {response}")
    return str(media_id)


def create_x_post(caption: str, media_id: str | None = None, reply_to: str | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"text": caption}
    if media_id:
        body["media"] = {"media_ids": [media_id]}
    if reply_to:
        body["reply"] = {"in_reply_to_tweet_id": reply_to}
    response, _ = request_json_with_headers(
        "POST",
        "https://api.x.com/2/tweets",
        x_headers(),
        body,
    )
    return response


def publish_x_post(caption: str, image_path: Path | None = None) -> dict[str, Any]:
    media_id = upload_x_image(image_path) if image_path else None
    response = create_x_post(caption, media_id)
    tweet = response.get("data", {})
    return {
        "id": tweet.get("id"),
        "url": f"https://x.com/i/web/status/{tweet.get('id')}" if tweet.get("id") else None,
        "response": response,
        "image": media_id,
    }


def read_x_thread(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8").strip()
    posts = [part.strip() for part in raw.split("\n---\n") if part.strip()]
    if not posts:
        raise PublishError(f"X thread file is empty: {path}")
    for index, post in enumerate(posts, 1):
        if len(post) > 280:
            raise PublishError(f"X thread post {index} exceeds 280 characters: {len(post)}")
    return posts


def publish_x_thread(posts: list[str]) -> dict[str, Any]:
    published = []
    previous_id = None
    for post in posts:
        response = create_x_post(post, reply_to=previous_id)
        tweet = response.get("data", {})
        tweet_id = tweet.get("id")
        if not tweet_id:
            raise PublishError(f"X thread post did not return an ID: {response}")
        published.append(
            {
                "id": tweet_id,
                "url": f"https://x.com/i/web/status/{tweet_id}",
                "response": response,
            }
        )
        previous_id = tweet_id
    return {"posts": published, "url": published[0]["url"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--carousel-dir", required=True)
    parser.add_argument("--public-base-url", required=True)
    parser.add_argument("--instagram-caption", required=True)
    parser.add_argument("--facebook-caption", required=True)
    parser.add_argument("--linkedin-caption")
    parser.add_argument("--x-caption")
    parser.add_argument("--x-thread")
    parser.add_argument(
        "--x-mode",
        choices=("auto", "short", "image", "thread"),
        default="auto",
        help="X publishing format. auto reads x-mode.txt next to --x-caption.",
    )
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
    linkedin_caption = None
    if args.linkedin_caption:
        linkedin_caption = Path(args.linkedin_caption).read_text(encoding="utf-8").strip()
        payload["linkedin_caption_length"] = len(linkedin_caption)
    x_caption = None
    x_mode = args.x_mode
    if args.x_caption:
        x_caption_path = Path(args.x_caption)
        x_caption = x_caption_path.read_text(encoding="utf-8").strip()
        payload["x_caption_length"] = len(x_caption)
        mode_path = x_caption_path.with_name("x-mode.txt")
        if x_mode == "auto" and mode_path.exists():
            x_mode = mode_path.read_text(encoding="utf-8").strip()
        elif x_mode == "auto":
            x_mode = "image"
        if x_mode not in {"short", "image", "thread"}:
            raise PublishError(f"Unsupported X mode: {x_mode}")
        payload["x_mode"] = x_mode
    x_thread_posts = None
    if args.x_thread:
        x_thread_posts = read_x_thread(Path(args.x_thread))
        payload["x_thread_count"] = len(x_thread_posts)
    if not args.dry_run:
        payload["instagram"] = publish_instagram_carousel(
            image_urls, Path(args.instagram_caption).read_text(encoding="utf-8").strip()
        )
        payload["facebook"] = publish_facebook_multiphoto(
            image_paths, Path(args.facebook_caption).read_text(encoding="utf-8").strip()
        )
        if linkedin_caption:
            payload["linkedin"] = publish_linkedin_post(image_paths[0], linkedin_caption)
        if x_caption:
            if x_mode == "short":
                payload["x"] = publish_x_post(x_caption)
            elif x_mode == "image":
                payload["x"] = publish_x_post(x_caption, image_paths[0])
            elif x_mode == "thread":
                if not x_thread_posts:
                    raise PublishError("X mode is thread but --x-thread was not provided.")
                payload["x"] = publish_x_thread(x_thread_posts)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
