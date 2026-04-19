from types import SimpleNamespace

from news_app import create_app
from news_app.db import get_connection, init_db
from news_app import rss_service


def fake_parse(_url):
    return SimpleNamespace(
        bozo=False,
        entries=[
            {
                "title": "Test news about Python",
                "summary": "<p>Short summary</p>",
                "link": "https://example.com/test-news",
                "published": "Fri, 18 Apr 2026 10:00:00 GMT",
                "author": "OpenAI",
                "category": "Test",
                "id": "news-1",
            }
        ],
    )


def run():
    init_db()
    rss_service.feedparser.parse = fake_parse
    updated_sources, inserted_items = rss_service.refresh_all_sources()
    assert updated_sources >= 1
    assert inserted_items >= 1

    app = create_app()
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    assert "Test news about Python" in response.get_data(as_text=True)

    response = client.get("/?q=Python")
    assert response.status_code == 200
    assert "Test news about Python" in response.get_data(as_text=True)

    with get_connection() as conn:
        row = conn.execute("SELECT id FROM news_items LIMIT 1").fetchone()
        assert row is not None
        item_id = row["id"]

    response = client.post(f"/saved/{item_id}/toggle", data={"next": "/"}, follow_redirects=True)
    assert response.status_code == 200
    assert "Список сохранённых обновлён" in response.get_data(as_text=True)

    response = client.get("/saved")
    assert response.status_code == 200
    assert "Test news about Python" in response.get_data(as_text=True)

    print("Smoke test passed")


if __name__ == "__main__":
    run()
