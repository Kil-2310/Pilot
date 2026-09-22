# App: accompanied

## Назначение
Приложение по работе с сопровождаемыми.
Модели БД описаны в файде ./models.py.

## URL

    | URL | View | Метод | Описание | Путь к HTML-шаблону |
    / | AccompaniedListView | GET | Получение ввсех сопровождаемых | accompanied/accompanied-list.html
    /detail/<pk>/ | AccompaniedDetailView | GET | Получение деталей сопровождаемого | accompanied/accompanied-detail.html
    /create/ | AccompaniedCreateView | POST | Создание нового сопровождаемого | accompanied/accompanied-create.html
    /update/<pk>/ | AccompaniedUpdateView | GET/POST | Обновление сопровождаемого | accompanied/accompanied-update.html

## Url для API
    
    | URL | ApiView | Метод | Описание |
    /persons-detail/<max_user_id>/ | AccompaniedListAPIView | GET | Получение всех сопровождаемых, привязанных к ответственному лицу
