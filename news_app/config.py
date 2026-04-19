from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = INSTANCE_DIR / "news.db"

DEFAULT_SETTINGS = {
    "items_per_page": "10",
    "update_interval_minutes": "30",
    "default_source_id": "",
}

DEFAULT_SOURCES = [
    {
        "name": "Habr",
        "rss_url": "https://habr.com/ru/rss/articles/?fl=ru",
        "category": "Технологии",
    },
    {
        "name": "Lenta.ru",
        "rss_url": "https://lenta.ru/rss",
        "category": "Общее",
    },
    {
        "name": "BBC UK",
        "rss_url": "http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml",
        "category": "Мир",
    },
]

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
NETWORK_TIMEOUT_SECONDS = int(os.getenv("NETWORK_TIMEOUT_SECONDS", "10"))
CACHE_TTL_MINUTES = int(os.getenv("CACHE_TTL_MINUTES", "30"))
MAX_ITEMS_PER_FEED = int(os.getenv("MAX_ITEMS_PER_FEED", "30"))
