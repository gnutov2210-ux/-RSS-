import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Iterable

from .config import DATABASE_PATH, DEFAULT_SETTINGS, DEFAULT_SOURCES


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rss_url TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT 'Общее',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS news_items (
                id TEXT PRIMARY KEY,
                source_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                link TEXT NOT NULL UNIQUE,
                published_at TEXT,
                author TEXT,
                category TEXT,
                fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                saved INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(source_id) REFERENCES sources(id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS cache_entries (
                cache_key TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
        _seed_defaults(conn)


def _seed_defaults(conn: sqlite3.Connection) -> None:
    for key, value in DEFAULT_SETTINGS.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    existing_count = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    if existing_count == 0:
        for source in DEFAULT_SOURCES:
            conn.execute(
                "INSERT INTO sources (name, rss_url, category, is_active) VALUES (?, ?, ?, 1)",
                (source["name"], source["rss_url"], source["category"]),
            )
    conn.commit()


def query_all(sql: str, params: Iterable = ()):  # type: ignore[override]
    with closing(get_connection()) as conn:
        return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: Iterable = ()):  # type: ignore[override]
    with closing(get_connection()) as conn:
        return conn.execute(sql, params).fetchone()


def execute(sql: str, params: Iterable = ()) -> None:  # type: ignore[override]
    with closing(get_connection()) as conn:
        conn.execute(sql, params)
        conn.commit()
