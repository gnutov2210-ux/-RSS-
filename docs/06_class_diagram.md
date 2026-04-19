# Этап 6. Диаграмма классов (текстовое описание)

**Файл:** `docs/06_class_diagram.md`

## Основные классы

### Presentation
- `NewsController`
  - обрабатывает запросы к главной странице, обновлению ленты и настройкам.
- `SettingsController`
  - показывает и сохраняет настройки.

### Application / Service
- `FeedService`
  - зависит от `IRssProvider`, `IFeedRepository`, `ISettingsStorage`, `ICachePolicy`.
  - выполняет загрузку RSS, дедупликацию, сортировку и возврат данных UI.
- `SettingsService`
  - зависит от `ISettingsStorage`.
  - валидирует и сохраняет настройки.

### Domain
- `NewsItem`
- `NewsSource`
- `FeedSnapshot`
- `AppSettings`
- `CachedEntry`

### Infrastructure
- `FeedparserRssProvider : IRssProvider`
  - использует библиотеку `feedparser`.
- `SqliteFeedRepository : IFeedRepository`
  - сохраняет и читает новости и снимки ленты из SQLite.
- `SqliteSettingsStorage : ISettingsStorage`
  - хранит настройки в SQLite или отдельной таблице.
- `TtlCachePolicy : ICachePolicy`
  - решает, можно ли использовать кэш.

## Связи между классами
- `NewsController` -> `FeedService`
- `SettingsController` -> `SettingsService`
- `FeedService` -> `IRssProvider`
- `FeedService` -> `IFeedRepository`
- `FeedService` -> `ISettingsStorage`
- `FeedService` -> `ICachePolicy`
- `SettingsService` -> `ISettingsStorage`
- `SqliteFeedRepository` -> `NewsItem`, `FeedSnapshot`
- `SqliteSettingsStorage` -> `AppSettings`
