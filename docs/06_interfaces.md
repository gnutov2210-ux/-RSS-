# Этап 6. Интерфейсы

**Файл:** `docs/06_interfaces.md`

## Ключевые интерфейсы

### IRssProvider
Назначение: загрузка и первичный парсинг RSS.

Методы:
- `fetch_feed(source: NewsSource) -> RssFeedDTO`
- `validate_source(source: NewsSource) -> bool`

### IFeedService
Назначение: сценарии работы с лентой новостей.

Методы:
- `get_feed(source_id: str, force_refresh: bool = False) -> FeedSnapshot`
- `filter_items(source_id: str, query: str) -> list[NewsItem]`
- `get_available_sources() -> list[NewsSource]`

### IFeedRepository
Назначение: хранение новостей и кэша.

Методы:
- `save_snapshot(snapshot: FeedSnapshot) -> None`
- `load_last_snapshot(source_id: str) -> FeedSnapshot | None`
- `save_news_items(items: list[NewsItem]) -> None`
- `get_news_by_source(source_id: str, limit: int) -> list[NewsItem]`

### ISettingsStorage
Назначение: чтение и запись настроек.

Методы:
- `load_settings() -> AppSettings`
- `save_settings(settings: AppSettings) -> None`

### ICachePolicy
Назначение: проверка срока действия кэша.

Методы:
- `is_expired(entry: CachedEntry, now: datetime) -> bool`
- `make_expiration(created_at: datetime, ttl_minutes: int) -> datetime`

## Типы ошибок уровня приложения
- `InvalidInputError` — пользователь передал некорректные параметры.
- `SourceNotFoundError` — выбранный источник отсутствует в конфиге.
- `NetworkError` — проблема сети, таймаут или недоступный хост.
- `InvalidFeedFormatError` — RSS не удалось разобрать или структура не поддерживается.
- `RateLimitedError` — внешний источник ограничил частоту запросов.
- `StorageError` — ошибка чтения/записи базы или файла настроек.
- `EmptyFeedError` — источник доступен, но не вернул ни одной новости.
