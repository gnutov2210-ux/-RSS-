# Архитектурный стиль

MVC (Model-View-Controller) на клиенте + Serverless функции (API Routes)

# Слои

- UI (Views / Components)
- Controller / Hooks (логика компонентов)
- Service (use cases: получение, фильтрация статей)
- Domain (модели Article, Source)
- Infrastructure (RSS парсер, LocalStorage кеш, API клиент)

# Модули

- Feed — загрузка и отображение ленты
- Article — детальный просмотр
- Favorites — управление избранным (чтение/запись в localStorage)
- Search — логика поиска
- Settings — управление настройками

# Правила зависимостей

- UI → Controller → Service → Domain → Infrastructure
- Обратные зависимости запрещены
