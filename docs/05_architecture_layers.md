# Этап 5. Архитектура уровня “слои и модули”

**Файл:** `docs/05_architecture_layers.md`

## 1. Архитектурный стиль
Для проекта используется простая слоистая архитектура в стиле **MVC / Service Layer**:
- Flask routes выступают как Controller,
- Jinja2 templates — View,
- сервисы и доменные модели — Application/Domain.

Такой подход подходит для учебного проекта: он проще MVVM для веба и не требует лишней сложности.

## 2. Слои

### UI / Presentation
- Flask routes
- HTML шаблоны Jinja2
- CSS

### Application / Service
- Сценарии: загрузить ленту, обновить источник, отфильтровать новости, сохранить настройки.

### Domain
- NewsItem, NewsSource, AppSettings, FeedSnapshot.
- Правила дедупликации, валидации и сортировки.

### Infrastructure
- HTTP‑клиент / feedparser для чтения RSS.
- SQLite repository.
- Конфигурация приложения.
- Логирование.

## 3. Модули и ответственность

### 1. WebModule
Отвечает за маршруты Flask, обработку HTTP‑запросов и передачу данных в шаблоны.

### 2. TemplateModule
Отвечает за HTML‑страницы: главную, настройки, страницу “О проекте”.

### 3. FeedServiceModule
Основной сервис приложения: загружает RSS, валидирует записи, удаляет дубли, сортирует новости.

### 4. SourceConfigModule
Хранит список разрешённых RSS‑источников и информацию о них.

### 5. SettingsServiceModule
Читает и сохраняет настройки приложения.

### 6. FeedRepositoryModule
Работает с SQLite: кэш лент, сохранение новостей, чтение последней успешной версии.

### 7. RssProviderModule
Инкапсулирует вызов `feedparser` и преобразование RSS в DTO.

### 8. LoggingModule
Логирует сетевые ошибки, ошибки парсинга и внутренние исключения.

## 4. Правило зависимостей
- UI зависит от Application и Domain.
- Application зависит от Domain и абстракций Infrastructure.
- Infrastructure реализует интерфейсы, объявленные на уровне Application/Domain.
- Domain не зависит от Flask, SQLite и RSS‑библиотек.
