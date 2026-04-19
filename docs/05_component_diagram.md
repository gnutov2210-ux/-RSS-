# Этап 5. Диаграмма компонентов

**Файл:** `docs/05_component_diagram.md`

## Компоненты системы

```text
[Browser]
    |
    v
[Flask Routes / Controllers]
    |
    +-----------------------> [Jinja2 Templates]
    |
    v
[FeedService]
    |           \
    |            \----> [SettingsService]
    | \
    |  \----> [RssProvider] ----> [External RSS Source]
    |
    \----> [FeedRepository / SQLite]
                     |
                     \----> [Cache Tables / Settings Tables]
```

## Краткое описание связей
- **Browser -> Flask Routes**: пользователь открывает страницы и отправляет запросы на обновление/фильтрацию.
- **Flask Routes -> Jinja2 Templates**: контроллеры передают данные во view.
- **Flask Routes -> FeedService**: основной сценарий получения и подготовки новостей.
- **FeedService -> RssProvider**: чтение RSS из внешнего источника.
- **FeedService -> FeedRepository**: сохранение и чтение кэша новостей.
- **FeedService -> SettingsService**: получение текущих настроек приложения.
- **RssProvider -> External RSS Source**: сетевой запрос к RSS‑ленте.
- **FeedRepository -> SQLite**: хранение кэша, настроек и метаданных обновления.

## Граница системы
Внутри системы находятся Flask, сервисы, шаблоны и SQLite. Внешними являются браузер пользователя и RSS‑источники.
