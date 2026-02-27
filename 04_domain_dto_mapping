# Domain-модели

- NewsSource, Article, Category, FavoriteArticle, FilterSettings

# DTO

- RssFeedDTO (сырые данные из RSS парсера), ArticleDTO, SourceDTO, SettingsDTO

# Инварианты

- Длина заголовка статьи не должна превышать 500 символов (обрезаем при парсинге)
- Максимальное количество статей для отображения на одной странице = 50
- Ссылка на источник должна быть валидным URL

# DTO → Domain

| DTO                     | Domain              | Преобразование                                 |
|-------------------------|---------------------|------------------------------------------------|
| RssFeedDTO.title        | Article.title       | Трим пробелов, декодинг HTML-сущностей         |
| RssFeedDTO.contentSnippet | Article.description | Если нет контента, используем заглушку         |
| RssFeedDTO.link         | Article.url         | Валидация URL                                   |
| RssFeedDTO.pubDate      | Article.publishedAt | Парсинг даты в единый формат (ISO)              |
