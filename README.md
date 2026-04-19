<<<<<<< HEAD
# RSS News

Простой учебный новостной сайт на **Flask + Jinja2 + feedparser + SQLite**.

## Что умеет
- загружать новости из RSS-источников;
- показывать список новостей на главной странице;
- фильтровать новости по источнику;
- искать новости по заголовку;
- открывать страницу одной новости;
- сохранять статьи в отдельный список;
- добавлять свои RSS-источники через UI и через CLI.

## Стек
- Python 3.11+
- Flask
- Jinja2
- feedparser
- SQLite
- простой CSS

## Быстрый запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

После запуска откройте в браузере:
- http://127.0.0.1:5000

## Полезные команды

```bash
# Запуск сайта
python app.py

# Загрузка новостей из RSS
python app.py fetch

# Список источников
python app.py sources list

# Добавление источника
python app.py sources add "Habr" https://habr.com/ru/rss/articles/?fl=ru --category "Технологии"

# Поиск новостей
python app.py search "python"

# Сохранённые статьи
python app.py saved list
python app.py saved add <news_id>

# Настройки
python app.py settings show
```

## Структура проекта

```text
news_rss_site/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── docs/
├── instance/
└── news_app/
    ├── __init__.py
    ├── config.py
    ├── db.py
    ├── rss_service.py
    ├── web.py
    ├── static/
    │   └── style.css
    └── templates/
        ├── base.html
        ├── index.html
        ├── article.html
        ├── sources.html
        ├── saved.html
        ├── settings.html
        └── 404.html
```

## Публикация на GitHub
1. Создайте репозиторий на GitHub.
2. Загрузите файлы проекта.
3. Добавьте `README.md` и `requirements.txt`.
4. Не загружайте папку `instance/` и локальную БД — она уже исключена через `.gitignore`.

## Важно
Если RSS-лента недоступна, приложение покажет ошибку. Для уже загруженных лент используется простой кэш в SQLite.
=======
# -RSS-
>>>>>>> 15bbab0c2d5a53189faadb5e9b2c3c631bd703a9
