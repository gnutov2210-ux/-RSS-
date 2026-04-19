# Этап 6. Диаграммы последовательностей

**Файл:** `docs/06_sequence_diagrams.md`

## 1. Пользователь открывает сайт -> загрузка новостей -> отображение

```text
Пользователь -> Browser: открывает /
Browser -> NewsController: GET /
NewsController -> FeedService: get_feed(default_source, force_refresh=false)
FeedService -> ISettingsStorage: load_settings()
FeedService -> IFeedRepository: load_last_snapshot(source_id)
alt кэш актуален
    IFeedRepository -> FeedService: FeedSnapshot
else кэш устарел или пуст
    FeedService -> IRssProvider: fetch_feed(source)
    IRssProvider -> External RSS: HTTP GET RSS
    External RSS -> IRssProvider: XML / RSS
    IRssProvider -> FeedService: RssFeedDTO
    FeedService -> FeedService: map DTO -> Domain, remove duplicates, sort by date
    FeedService -> IFeedRepository: save_snapshot(snapshot)
end
FeedService -> NewsController: FeedSnapshot
NewsController -> Browser: HTML с новостями
Browser -> Пользователь: отображение списка новостей
```

## 2. Пользователь выбирает другой источник -> обновление -> отображение

```text
Пользователь -> Browser: выбирает источник и нажимает "Обновить"
Browser -> NewsController: POST /refresh {source_id}
NewsController -> FeedService: get_feed(source_id, force_refresh=true)
FeedService -> IRssProvider: fetch_feed(source)
IRssProvider -> External RSS: HTTP GET RSS
External RSS -> IRssProvider: XML / RSS или ошибка
alt успех
    IRssProvider -> FeedService: RssFeedDTO
    FeedService -> FeedService: map DTO -> Domain, remove duplicates
    FeedService -> IFeedRepository: save_snapshot(snapshot)
    FeedService -> NewsController: FeedSnapshot
    NewsController -> Browser: HTML / redirect с обновлённой лентой
else ошибка сети / формат
    IRssProvider -> FeedService: exception
    FeedService -> IFeedRepository: load_last_snapshot(source_id)
    alt есть сохранённый кэш
        IFeedRepository -> FeedService: FeedSnapshot
        FeedService -> NewsController: snapshot + warning
    else кэша нет
        FeedService -> NewsController: app error
    end
    NewsController -> Browser: страница с сообщением об ошибке
end
Browser -> Пользователь: видит новую ленту или сообщение
```
