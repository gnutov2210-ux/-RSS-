from __future__ import annotations

import hashlib
import html
import json
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Optional
from urllib.parse import urlparse

import feedparser

from .config import CACHE_TTL_MINUTES, MAX_ITEMS_PER_FEED, NETWORK_TIMEOUT_SECONDS
from .db import get_connection

TAG_RE = re.compile(r"<[^>]+>")


class RssServiceError(Exception):
    pass


class InvalidFeedError(RssServiceError):
    pass


def sanitize_html(text: Optional[str]) -> str:
    if not text:
        return ""
    cleaned = TAG_RE.sub(" ", text)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise InvalidFeedError("Неверный RSS URL. Используйте http/https адрес.")
    return url.strip()


def entry_id(entry: Any) -> str:
    raw = entry.get("id") or entry.get("guid") or entry.get("link") or entry.get("title")
    raw = str(raw).strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def extract_summary(entry: Any) -> str:
    candidates: list[str] = []

    for key in ("summary", "description"):
        value = entry.get(key)
        if value:
            candidates.append(str(value))

    summary_detail = entry.get("summary_detail")
    if isinstance(summary_detail, dict):
        value = summary_detail.get("value")
        if value:
            candidates.append(str(value))

    content_blocks = entry.get("content") or []
    if isinstance(content_blocks, list):
        for block in content_blocks:
            if isinstance(block, dict) and block.get("value"):
                candidates.append(str(block.get("value")))

    for candidate in candidates:
        cleaned = sanitize_html(candidate)
        if cleaned:
            return cleaned[:500]

    return "Краткое описание временно недоступно. Откройте оригинал статьи."


def parse_published(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return None


def fetch_feed(source_row) -> dict[str, Any]:
    rss_url = source_row["rss_url"]
    cache_key = f"feed:{source_row['id']}"
    cached_payload = _get_cached_payload(cache_key)

    try:
        parsed = feedparser.parse(rss_url)
    except Exception as exc:
        if cached_payload:
            return {"from_cache": True, "items": cached_payload}
        raise RssServiceError(f"Не удалось прочитать RSS-ленту: {exc}") from exc

    if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", None):
        if cached_payload:
            return {"from_cache": True, "items": cached_payload}
        raise InvalidFeedError("RSS-лента недоступна или имеет неверный формат.")

    entries = parsed.entries[:MAX_ITEMS_PER_FEED]
    items = []
    for entry in entries:
        title = str(entry.get("title", "")).strip() or "Без заголовка"
        summary = extract_summary(entry)
        link = str(entry.get("link", "")).strip()
        if not link:
            continue
        item = {
            "id": entry_id(entry),
            "title": title,
            "summary": summary,
            "link": link,
            "published_at": parse_published(entry.get("published") or entry.get("updated")),
            "author": (str(entry.get("author")).strip() if entry.get("author") else None),
            "category": _entry_category(entry),
        }
        items.append(item)

    _set_cached_payload(cache_key, items)
    return {"from_cache": False, "items": items}


def refresh_all_sources(source_id: Optional[int] = None) -> tuple[int, int]:
    with get_connection() as conn:
        if source_id is None:
            sources = conn.execute(
                "SELECT * FROM sources WHERE is_active = 1 ORDER BY id"
            ).fetchall()
        else:
            sources = conn.execute(
                "SELECT * FROM sources WHERE id = ? AND is_active = 1", (source_id,)
            ).fetchall()

    updated_sources = 0
    inserted_items = 0
    for source in sources:
        result = fetch_feed(source)
        with get_connection() as conn:
            for item in result["items"]:
                conn.execute(
                    """
                    INSERT INTO news_items (id, source_id, title, summary, link, published_at, author, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        title = excluded.title,
                        summary = excluded.summary,
                        link = excluded.link,
                        published_at = excluded.published_at,
                        author = excluded.author,
                        category = excluded.category,
                        fetched_at = CURRENT_TIMESTAMP
                    """,
                    (
                        item["id"],
                        source["id"],
                        item["title"],
                        item["summary"],
                        item["link"],
                        item["published_at"],
                        item["author"],
                        item["category"],
                    ),
                )
                inserted_items += 1
            conn.commit()
        updated_sources += 1
    return updated_sources, inserted_items


def _entry_category(entry: Any) -> str:
    tags = entry.get("tags") or []
    if tags:
        term = tags[0].get("term") if isinstance(tags[0], dict) else None
        if term:
            return str(term)
    category = entry.get("category")
    return str(category).strip() if category else "Общее"


def _get_cached_payload(cache_key: str) -> Optional[list[dict[str, Any]]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT payload, expires_at FROM cache_entries WHERE cache_key = ?",
            (cache_key,),
        ).fetchone()
        if not row:
            return None
        try:
            expires_at = datetime.fromisoformat(row["expires_at"])
            if expires_at < datetime.now(timezone.utc):
                return None
            return json.loads(row["payload"])
        except Exception:
            return None


def _set_cached_payload(cache_key: str, payload: list[dict[str, Any]]) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=CACHE_TTL_MINUTES)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO cache_entries (cache_key, payload, expires_at)
            VALUES (?, ?, ?)
            ON CONFLICT(cache_key) DO UPDATE SET
                payload = excluded.payload,
                created_at = CURRENT_TIMESTAMP,
                expires_at = excluded.expires_at
            """,
            (cache_key, json.dumps(payload, ensure_ascii=False), expires_at.isoformat()),
        )
        conn.commit()
