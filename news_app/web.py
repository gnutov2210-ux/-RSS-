from __future__ import annotations

from datetime import datetime
from math import ceil

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from .config import SECRET_KEY
from .db import execute, get_connection, init_db
from .rss_service import InvalidFeedError, RssServiceError, normalize_url, refresh_all_sources


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = SECRET_KEY
    init_db()

    @app.context_processor
    def inject_now():
        return {"current_year": datetime.now().year}

    @app.route("/")
    def index():
        page = max(request.args.get("page", default=1, type=int), 1)
        source_id = request.args.get("source_id", type=int)
        q = (request.args.get("q") or "").strip()
        per_page = get_setting_int("items_per_page", 10)
        offset = (page - 1) * per_page

        where = []
        params = []
        if source_id:
            where.append("news_items.source_id = ?")
            params.append(source_id)
        if q:
            where.append("LOWER(news_items.title) LIKE ?")
            params.append(f"%{q.lower()}%")

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        with get_connection() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM news_items {where_sql}", params
            ).fetchone()[0]
            items = conn.execute(
                f"""
                SELECT news_items.*, sources.name AS source_name
                FROM news_items
                JOIN sources ON sources.id = news_items.source_id
                {where_sql}
                ORDER BY COALESCE(news_items.published_at, news_items.fetched_at) DESC
                LIMIT ? OFFSET ?
                """,
                [*params, per_page, offset],
            ).fetchall()
            sources = conn.execute(
                "SELECT * FROM sources ORDER BY name"
            ).fetchall()

        total_pages = max(ceil(total / per_page), 1)
        return render_template(
            "index.html",
            items=items,
            sources=sources,
            page=page,
            total_pages=total_pages,
            selected_source_id=source_id,
            query=q,
        )

    @app.route("/article/<item_id>")
    def article_detail(item_id: str):
        with get_connection() as conn:
            item = conn.execute(
                """
                SELECT news_items.*, sources.name AS source_name
                FROM news_items
                JOIN sources ON sources.id = news_items.source_id
                WHERE news_items.id = ?
                """,
                (item_id,),
            ).fetchone()
        if not item:
            abort(404)
        return render_template("article.html", item=item)

    @app.route("/sources")
    def sources_page():
        with get_connection() as conn:
            sources = conn.execute(
                "SELECT * FROM sources ORDER BY created_at DESC, name"
            ).fetchall()
        return render_template("sources.html", sources=sources)

    @app.post("/sources/add")
    def sources_add():
        name = (request.form.get("name") or "").strip()
        rss_url = (request.form.get("rss_url") or "").strip()
        category = (request.form.get("category") or "Общее").strip()
        if not name:
            flash("Введите название источника.", "error")
            return redirect(url_for("sources_page"))
        try:
            rss_url = normalize_url(rss_url)
        except InvalidFeedError as exc:
            flash(str(exc), "error")
            return redirect(url_for("sources_page"))

        try:
            execute(
                "INSERT INTO sources (name, rss_url, category, is_active) VALUES (?, ?, ?, 1)",
                (name, rss_url, category),
            )
            flash("Источник добавлен.", "success")
        except Exception:
            flash("Не удалось добавить источник. Возможно, такой URL уже существует.", "error")
        return redirect(url_for("sources_page"))

    @app.post("/sources/<int:source_id>/toggle")
    def source_toggle(source_id: int):
        with get_connection() as conn:
            row = conn.execute("SELECT is_active FROM sources WHERE id = ?", (source_id,)).fetchone()
            if not row:
                abort(404)
            new_value = 0 if row["is_active"] else 1
            conn.execute("UPDATE sources SET is_active = ? WHERE id = ?", (new_value, source_id))
            conn.commit()
        flash("Статус источника обновлён.", "success")
        return redirect(url_for("sources_page"))

    @app.post("/fetch")
    def fetch_now():
        try:
            updated_sources, inserted_items = refresh_all_sources()
            flash(f"Обновление завершено: источников {updated_sources}, записей обработано {inserted_items}.", "success")
        except (RssServiceError, InvalidFeedError) as exc:
            flash(str(exc), "error")
        return redirect(url_for("index"))

    @app.post("/saved/<item_id>/toggle")
    def saved_toggle(item_id: str):
        with get_connection() as conn:
            row = conn.execute("SELECT saved FROM news_items WHERE id = ?", (item_id,)).fetchone()
            if not row:
                abort(404)
            new_value = 0 if row["saved"] else 1
            conn.execute("UPDATE news_items SET saved = ? WHERE id = ?", (new_value, item_id))
            conn.commit()
        flash("Список сохранённых обновлён.", "success")
        next_url = request.form.get("next") or url_for("index")
        return redirect(next_url)

    @app.route("/saved")
    def saved_page():
        with get_connection() as conn:
            items = conn.execute(
                """
                SELECT news_items.*, sources.name AS source_name
                FROM news_items
                JOIN sources ON sources.id = news_items.source_id
                WHERE news_items.saved = 1
                ORDER BY COALESCE(news_items.published_at, news_items.fetched_at) DESC
                """
            ).fetchall()
        return render_template("saved.html", items=items)

    @app.route("/settings")
    def settings_page():
        with get_connection() as conn:
            settings_rows = conn.execute("SELECT key, value FROM settings ORDER BY key").fetchall()
        settings = {row["key"]: row["value"] for row in settings_rows}
        return render_template("settings.html", settings=settings)

    @app.post("/settings")
    def settings_update():
        items_per_page = max(min(request.form.get("items_per_page", type=int, default=10), 50), 1)
        update_interval = max(min(request.form.get("update_interval_minutes", type=int, default=30), 1440), 1)
        set_setting("items_per_page", str(items_per_page))
        set_setting("update_interval_minutes", str(update_interval))
        flash("Настройки сохранены.", "success")
        return redirect(url_for("settings_page"))

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    return app


def get_setting_int(key: str, default: int) -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if not row:
        return default
    try:
        return int(row["value"])
    except (ValueError, TypeError):
        return default


def set_setting(key: str, value: str) -> None:
    execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
