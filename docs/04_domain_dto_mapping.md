# Этап 4. Модель предметной области + DTO + маппинг

**Файл:** `docs/04_domain_dto_mapping.md`

## Domain-модели

### NewsSource
- `id`
- `name`
- `rss_url`
- `category`
- `is_active`

Описание: источник новостей, из которого приложение получает RSS-ленту.

### NewsItem
- `id`
- `source_id`
- `title`
- `summary`
- `link`
- `published_at`
- `author`
- `category`

Описание: одна новость, полученная из RSS-ленты и используемая внутри приложения.

### AppSettings
- `items_per_page`
- `update_interval_minutes`
- `default_source_id`

Описание: настройки приложения, влияющие на отображение и обновление новостей.

### CachedEntry
- `cache_key`
- `payload`
- `created_at`
- `expires_at`

Описание: запись локального кэша, используемая для временного хранения результатов загрузки RSS-ленты.

### SavedArticle
- `news_id`
- `saved_at`

Описание: сохранённая пользователем статья для быстрого доступа.

## DTO (внешние данные)

### RssFeedDTO
Сырые данные RSS-ленты, полученные через библиотеку `feedparser`.

### RssEntryDTO
Одна запись из RSS-ленты:
- `title`
- `summary` / `description`
- `link`
- `published`
- `id` / `guid`
- `author`
- `category`

### SettingsFileDTO
Объект настроек приложения:
- `items_per_page`
- `update_interval_minutes`
- `default_source_id`

### SavedArticlesFileDTO
Список сохранённых пользователем статей:
- `news_id`
- `saved_at`

### CacheFileDTO
Представление сохранённой RSS-ленты в кэше:
- `cache_key`
- `payload`
- `created_at`
- `expires_at`

## Инварианты и ограничения данных
- Название источника (`name`) не может быть пустой строкой.
- RSS URL (`rss_url`) должен быть корректным HTTP/HTTPS-адресом.
- Заголовок новости (`title`) не может быть пустой строкой после удаления пробелов.
- Ссылка на новость (`link`) не может быть пустой строкой.
- Количество новостей на странице: `1 <= items_per_page <= 50`.
- Интервал обновления ленты: `1 <= update_interval_minutes <= 1440`.
- Если `guid` отсутствует, в качестве идентификатора новости используется `link`.
- В пределах одного источника не должно быть двух новостей с одинаковым `id`.

## Таблица “DTO -> Domain”

| DTO поле | Domain поле | Преобразование / правило |
|---|---|---|
| `RssEntryDTO.id` / `guid` | `NewsItem.id` | Используется напрямую; если отсутствует, берётся `link`. |
| `RssEntryDTO.title` | `NewsItem.title` | Прямое присвоение после удаления лишних пробелов. |
| `RssEntryDTO.summary` / `description` | `NewsItem.summary` | Берётся `summary`, если его нет — `description`. |
| `RssEntryDTO.link` | `NewsItem.link` | Прямое присвоение. |
| `RssEntryDTO.published` | `NewsItem.published_at` | Преобразование строки даты RSS в `datetime`; если дата отсутствует или не распознана — `None`. |
| `RssEntryDTO.author` | `NewsItem.author` | Прямое присвоение; если поле отсутствует — `None`. |
| `RssEntryDTO.category` | `NewsItem.category` | Прямое присвоение; если поле отсутствует — `"Общее"`. |
| `SettingsFileDTO.items_per_page` | `AppSettings.items_per_page` | Если значение вне диапазона `1..50`, используется значение по умолчанию `10`. |
| `SettingsFileDTO.update_interval_minutes` | `AppSettings.update_interval_minutes` | Если значение вне диапазона `1..1440`, используется значение по умолчанию `30`. |
| `SettingsFileDTO.default_source_id` | `AppSettings.default_source_id` | Прямое присвоение; если значение отсутствует — `None`. |
| `CacheFileDTO.payload` | `CachedEntry.payload` | Прямое присвоение в виде строки JSON/XML. |
| `SavedArticlesFileDTO.news_id` | `SavedArticle.news_id` | Прямое присвоение. |
