# 06_design_details.md

## Основные классы (Class Diagram)

- Article, NewsSource, Category, FavoriteService
- FeedController, SearchController, FavoritesView, FeedView

## Интерфейсы

- IFeedProvider — загрузка и парсинг RSS лент
- IStorage — сохранение избранного и настроек в LocalStorage
- ICache — кеширование загруженных статей в памяти
- Ошибки: NetworkError, ParseError, EmptyFeedError, InvalidSourceError

## Диаграммы последовательности (Sequence Diagrams)

### Сценарий 1: Загрузка ленты
Пользователь открывает сайт → FeedController → FeedService (запрос к нескольким RSS провайдерам) → Парсинг данных → Обновление UI (рендер карточек)

### Сценарий 2: Добавление в избранное
Пользователь кликает "В избранное" → FavoritesController → FavoritesService (запись в LocalStorage) → Обновление состояния иконки в UI
