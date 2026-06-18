#!/usr/bin/env python3
"""Publish one post to Facebook Pages, Instagram, and LinkedIn."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DEFAULT_ENV_FILE = ROOT / ".env"


class PublisherError(RuntimeError):
    pass


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise PublisherError(f"Missing required setting: {name}")
    return value


def redact(value: str) -> str:
    if len(value) < 10:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
    raw_body: bytes | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    request_headers = {"User-Agent": "social-publisher/1.0"}
    request_headers.update(headers or {})

    body = raw_body
    if data is not None:
        if request_headers.get("Content-Type") == "application/json":
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        else:
            body = urlencode(data).encode("utf-8")
            request_headers.setdefault(
                "Content-Type", "application/x-www-form-urlencoded"
            )

    request = Request(url, data=body, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            payload = response.read()
            parsed = json.loads(payload.decode("utf-8")) if payload else {}
            return parsed, dict(response.headers.items())
    except HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(payload)
        except json.JSONDecodeError:
            detail = payload
        raise PublisherError(
            f"{method} {url} failed with HTTP {error.code}: {detail}"
        ) from error
    except URLError as error:
        raise PublisherError(f"{method} {url} failed: {error.reason}") from error


def request_bytes(
    method: str,
    url: str,
    body: bytes,
    *,
    headers: dict[str, str] | None = None,
) -> dict[str, str]:
    request_headers = {"User-Agent": "social-publisher/1.0"}
    request_headers.update(headers or {})
    request = Request(url, data=body, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=120) as response:
            response.read()
            return dict(response.headers.items())
    except HTTPError as error:
        payload = error.read().decode("utf-8", errors="replace")
        raise PublisherError(
            f"{method} upload failed with HTTP {error.code}: {payload}"
        ) from error
    except URLError as error:
        raise PublisherError(f"{method} upload failed: {error.reason}") from error


def multipart_body(
    fields: dict[str, str], file_field: str, file_path: Path
) -> tuple[bytes, str]:
    boundary = f"----social-publisher-{uuid.uuid4().hex}"
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


def meta_base() -> str:
    version = os.getenv("META_GRAPH_VERSION", "v25.0").strip()
    return f"https://graph.facebook.com/{version}"


def discover_meta() -> list[dict[str, Any]]:
    user_token = require_env("META_USER_ACCESS_TOKEN")
    query = urlencode(
        {
            "fields": (
                "id,name,access_token,tasks,"
                "instagram_business_account{id,username,name}"
            ),
            "access_token": user_token,
        }
    )
    response, _ = request_json("GET", f"{meta_base()}/me/accounts?{query}")
    channels: list[dict[str, Any]] = []
    for page in response.get("data", []):
        channels.append(
            {
                "channel": "facebook",
                "id": page.get("id"),
                "name": page.get("name"),
                "tasks": page.get("tasks", []),
                "page_access_token": page.get("access_token"),
            }
        )
        instagram = page.get("instagram_business_account")
        if instagram:
            channels.append(
                {
                    "channel": "instagram",
                    "id": instagram.get("id"),
                    "username": instagram.get("username"),
                    "name": instagram.get("name"),
                    "connected_facebook_page_id": page.get("id"),
                }
            )
    return channels


def discover_linkedin() -> list[dict[str, Any]]:
    token = require_env("LINKEDIN_ACCESS_TOKEN")
    response, _ = request_json(
        "GET",
        "https://api.linkedin.com/v2/me",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    person_id = response.get("id")
    if not person_id:
        raise PublisherError(f"LinkedIn did not return a person ID: {response}")
    return [
        {
            "channel": "linkedin",
            "id": person_id,
            "author_urn": f"urn:li:person:{person_id}",
            "name": " ".join(
                value
                for value in (
                    response.get("localizedFirstName"),
                    response.get("localizedLastName"),
                )
                if value
            ),
            "vanity_name": response.get("vanityName"),
        }
    ]


def publish_facebook(
    text: str, image_path: Path | None, image_url: str | None
) -> dict[str, Any]:
    page_id = require_env("FACEBOOK_PAGE_ID")
    token = require_env("FACEBOOK_PAGE_ACCESS_TOKEN")
    endpoint = f"{meta_base()}/{page_id}/photos" if image_path or image_url else (
        f"{meta_base()}/{page_id}/feed"
    )

    if image_path:
        body, boundary = multipart_body(
            {"message": text, "access_token": token}, "source", image_path
        )
        response, _ = request_json(
            "POST",
            endpoint,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            raw_body=body,
        )
        return response

    data = {"message": text, "access_token": token}
    if image_url:
        data["url"] = image_url
    response, _ = request_json("POST", endpoint, data=data)
    return response


def publish_instagram(text: str, image_url: str | None) -> dict[str, Any]:
    if not image_url or not image_url.startswith("https://"):
        raise PublisherError(
            "Instagram requires --image-url with a public HTTPS image URL."
        )
    account_id = require_env("INSTAGRAM_ACCOUNT_ID")
    token = require_env("INSTAGRAM_ACCESS_TOKEN")

    container, _ = request_json(
        "POST",
        f"{meta_base()}/{account_id}/media",
        data={"image_url": image_url, "caption": text, "access_token": token},
    )
    creation_id = container.get("id")
    if not creation_id:
        raise PublisherError(f"Instagram did not return a creation ID: {container}")

    for _ in range(10):
        query = urlencode(
            {"fields": "status_code,status", "access_token": token}
        )
        status, _ = request_json(
            "GET", f"{meta_base()}/{creation_id}?{query}"
        )
        status_code = status.get("status_code")
        if status_code == "FINISHED":
            break
        if status_code in {"ERROR", "EXPIRED"}:
            raise PublisherError(f"Instagram container failed: {status}")
        time.sleep(3)
    else:
        raise PublisherError("Instagram media container did not finish in time.")

    result, _ = request_json(
        "POST",
        f"{meta_base()}/{account_id}/media_publish",
        data={"creation_id": creation_id, "access_token": token},
    )
    return result


def linkedin_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {require_env('LINKEDIN_ACCESS_TOKEN')}",
        "Linkedin-Version": os.getenv("LINKEDIN_VERSION", "202605"),
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def upload_linkedin_image(image_path: Path, owner: str) -> str:
    initialized, _ = request_json(
        "POST",
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers=linkedin_headers(),
        data={"initializeUploadRequest": {"owner": owner}},
    )
    value = initialized.get("value", {})
    upload_url = value.get("uploadUrl")
    image_urn = value.get("image")
    if not upload_url or not image_urn:
        raise PublisherError(f"LinkedIn image initialization failed: {initialized}")

    request_bytes(
        "PUT",
        upload_url,
        image_path.read_bytes(),
        headers={
            "Authorization": f"Bearer {require_env('LINKEDIN_ACCESS_TOKEN')}",
            "Content-Type": (
                mimetypes.guess_type(image_path.name)[0]
                or "application/octet-stream"
            ),
        },
    )
    return image_urn


def publish_linkedin(text: str, image_path: Path | None) -> dict[str, Any]:
    author = require_env("LINKEDIN_AUTHOR_URN")
    payload: dict[str, Any] = {
        "author": author,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if image_path:
        image_urn = upload_linkedin_image(image_path, author)
        payload["content"] = {
            "media": {"id": image_urn, "title": image_path.stem}
        }

    response, headers = request_json(
        "POST",
        "https://api.linkedin.com/rest/posts",
        headers=linkedin_headers(),
        data=payload,
    )
    post_id = next(
        (
            value
            for key, value in headers.items()
            if key.lower() == "x-restli-id"
        ),
        None,
    )
    return {"id": post_id, "response": response}


def resolve_image(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise PublisherError(f"Image file not found: {path}")
    return path


def read_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.text_file:
        path = Path(args.text_file).expanduser().resolve()
        return path.read_text(encoding="utf-8-sig").strip()
    raise PublisherError("Provide --text or --text-file.")


def configured_channels() -> dict[str, dict[str, str]]:
    return {
        "facebook": {
            "FACEBOOK_PAGE_ID": os.getenv("FACEBOOK_PAGE_ID", ""),
            "FACEBOOK_PAGE_ACCESS_TOKEN": os.getenv(
                "FACEBOOK_PAGE_ACCESS_TOKEN", ""
            ),
        },
        "instagram": {
            "INSTAGRAM_ACCOUNT_ID": os.getenv("INSTAGRAM_ACCOUNT_ID", ""),
            "INSTAGRAM_ACCESS_TOKEN": os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        },
        "linkedin": {
            "LINKEDIN_AUTHOR_URN": os.getenv("LINKEDIN_AUTHOR_URN", ""),
            "LINKEDIN_ACCESS_TOKEN": os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
        },
    }


def setting_is_present(key: str, value: str) -> bool:
    normalized = value.strip()
    if not normalized:
        return False
    if key == "LINKEDIN_AUTHOR_URN":
        return normalized not in {"urn:li:person:", "urn:li:organization:"}
    return True


def command_doctor() -> int:
    rows = []
    for channel, values in configured_channels().items():
        missing = [
            key
            for key, value in values.items()
            if not setting_is_present(key, value)
        ]
        rows.append(
            {
                "channel": channel,
                "ready": not missing,
                "missing": missing,
                "identity": next(
                    (
                        value
                        for key, value in values.items()
                        if key.endswith("_ID") or key.endswith("_URN")
                    ),
                    "",
                ),
            }
        )
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0 if all(row["ready"] for row in rows) else 1


def command_discover(platform: str) -> int:
    channels: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    if platform in {"all", "meta"}:
        try:
            channels.extend(discover_meta())
        except PublisherError as error:
            errors["meta"] = str(error)
    if platform in {"all", "linkedin"}:
        try:
            channels.extend(discover_linkedin())
        except PublisherError as error:
            errors["linkedin"] = str(error)

    safe_channels = []
    for channel in channels:
        safe = dict(channel)
        if safe.get("page_access_token"):
            safe["page_access_token"] = redact(safe["page_access_token"])
        safe_channels.append(safe)
    print(
        json.dumps(
            {"channels": safe_channels, "errors": errors},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if channels else 1


def command_publish(args: argparse.Namespace) -> int:
    text = read_text(args)
    image_path = resolve_image(args.image)
    selected = [item.strip() for item in args.channels.split(",") if item.strip()]
    supported = {"facebook", "instagram", "linkedin"}
    invalid = sorted(set(selected) - supported)
    if invalid:
        raise PublisherError(f"Unsupported channels: {', '.join(invalid)}")

    preview = {
        "channels": selected,
        "text_length": len(text),
        "image": str(image_path) if image_path else None,
        "image_url": args.image_url,
    }
    if args.dry_run:
        print(json.dumps({"dry_run": True, **preview}, ensure_ascii=False, indent=2))
        return 0

    results: dict[str, Any] = {}
    for channel in selected:
        if channel == "facebook":
            results[channel] = publish_facebook(text, image_path, args.image_url)
        elif channel == "instagram":
            results[channel] = publish_instagram(text, args.image_url)
        elif channel == "linkedin":
            results[channel] = publish_linkedin(text, image_path)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish content through official social platform APIs."
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Path to the environment file (default: .env)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Check whether channel settings exist.")
    discover = subparsers.add_parser(
        "discover", help="Discover Facebook Pages and connected Instagram accounts."
    )
    discover.add_argument(
        "--platform",
        choices=("all", "meta", "linkedin"),
        default="all",
        help="Platform to inspect (default: all).",
    )
    publish = subparsers.add_parser("publish", help="Publish a social post.")
    publish.add_argument(
        "--channels",
        default="facebook,instagram,linkedin",
        help="Comma-separated channel names.",
    )
    text_group = publish.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text")
    text_group.add_argument("--text-file")
    publish.add_argument("--image", help="Local image for Facebook and LinkedIn.")
    publish.add_argument(
        "--image-url", help="Public HTTPS image URL required by Instagram."
    )
    publish.add_argument(
        "--dry-run", action="store_true", help="Validate inputs without publishing."
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    load_env(Path(args.env_file).expanduser().resolve())
    try:
        if args.command == "doctor":
            return command_doctor()
        if args.command == "discover":
            return command_discover(args.platform)
        if args.command == "publish":
            return command_publish(args)
        parser.error(f"Unknown command: {args.command}")
    except PublisherError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
