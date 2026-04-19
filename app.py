from __future__ import annotations

import argparse

from news_app import create_app
from news_app.db import execute, get_connection, init_db
from news_app.rss_service import InvalidFeedError, RssServiceError, normalize_url, refresh_all_sources

app = create_app()


def run_server(args) -> None:
    app.run(debug=args.debug, host=args.host, port=args.port)


def cmd_fetch(args) -> None:
    init_db()
    source_id = args.source_id
    updated_sources, inserted_items = refresh_all_sources(source_id=source_id)
    print(f"Готово: источников обновлено {updated_sources}, записей обработано {inserted_items}.")


def cmd_sources_list(_args) -> None:
    init_db()
    with get_connection() as conn:
        rows = conn.execute("SELECT id, name, rss_url, category, is_active FROM sources ORDER BY id").fetchall()
    if not rows:
        print("Источники не найдены.")
        return
    for row in rows:
        status = "active" if row["is_active"] else "inactive"
        print(f"[{row['id']}] {row['name']} ({row['category']}) - {status}\n    {row['rss_url']}")


def cmd_sources_add(args) -> None:
    init_db()
    rss_url = normalize_url(args.rss_url)
    execute(
        "INSERT INTO sources (name, rss_url, category, is_active) VALUES (?, ?, ?, 1)",
        (args.name, rss_url, args.category),
    )
    print("Источник добавлен.")


def cmd_search(args) -> None:
    init_db()
    query = f"%{args.query.lower()}%"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT news_items.id, news_items.title, news_items.link, sources.name AS source_name
            FROM news_items
            JOIN sources ON sources.id = news_items.source_id
            WHERE LOWER(news_items.title) LIKE ?
            ORDER BY COALESCE(news_items.published_at, news_items.fetched_at) DESC
            LIMIT 20
            """,
            (query,),
        ).fetchall()
    if not rows:
        print("Ничего не найдено. Сначала выполните: python app.py fetch")
        return
    for row in rows:
        print(f"- {row['title']}\n  [{row['source_name']}] {row['link']}\n  id={row['id']}")


def cmd_saved_list(_args) -> None:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, link FROM news_items WHERE saved = 1 ORDER BY fetched_at DESC"
        ).fetchall()
    if not rows:
        print("Сохранённых статей нет.")
        return
    for row in rows:
        print(f"- {row['title']}\n  {row['link']}\n  id={row['id']}")


def cmd_saved_add(args) -> None:
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT id FROM news_items WHERE id = ?", (args.news_id,)).fetchone()
        if not row:
            print("Новость не найдена.")
            return
        conn.execute("UPDATE news_items SET saved = 1 WHERE id = ?", (args.news_id,))
        conn.commit()
    print("Статья сохранена.")


def cmd_settings_show(_args) -> None:
    init_db()
    with get_connection() as conn:
        rows = conn.execute("SELECT key, value FROM settings ORDER BY key").fetchall()
    for row in rows:
        print(f"{row['key']} = {row['value']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Простой новостной сайт с RSS на Flask")
    subparsers = parser.add_subparsers(dest="command")

    fetch_parser = subparsers.add_parser("fetch", help="Загрузить новости из RSS")
    fetch_parser.add_argument("--source-id", type=int, default=None, help="Обновить только один источник по ID")
    fetch_parser.set_defaults(func=cmd_fetch)

    sources_parser = subparsers.add_parser("sources", help="Работа с источниками")
    sources_sub = sources_parser.add_subparsers(dest="sources_command")

    sources_list = sources_sub.add_parser("list", help="Показать список источников")
    sources_list.set_defaults(func=cmd_sources_list)

    sources_add = sources_sub.add_parser("add", help="Добавить источник")
    sources_add.add_argument("name")
    sources_add.add_argument("rss_url")
    sources_add.add_argument("--category", default="Общее")
    sources_add.set_defaults(func=cmd_sources_add)

    search_parser = subparsers.add_parser("search", help="Поиск новостей")
    search_parser.add_argument("query")
    search_parser.set_defaults(func=cmd_search)

    saved_parser = subparsers.add_parser("saved", help="Сохранённые статьи")
    saved_sub = saved_parser.add_subparsers(dest="saved_command")

    saved_list = saved_sub.add_parser("list", help="Показать сохранённые статьи")
    saved_list.set_defaults(func=cmd_saved_list)

    saved_add = saved_sub.add_parser("add", help="Сохранить статью по ID")
    saved_add.add_argument("news_id")
    saved_add.set_defaults(func=cmd_saved_add)

    settings_parser = subparsers.add_parser("settings", help="Показать настройки")
    settings_sub = settings_parser.add_subparsers(dest="settings_command")
    settings_show = settings_sub.add_parser("show", help="Показать настройки")
    settings_show.set_defaults(func=cmd_settings_show)

    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        run_server(args)
        return

    try:
        args.func(args)
    except (RssServiceError, InvalidFeedError) as exc:
        print(f"Ошибка: {exc}")
    except AttributeError:
        parser.print_help()


if __name__ == "__main__":
    main()
