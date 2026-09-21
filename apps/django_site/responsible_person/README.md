# App: responsible_person

## Назначение
Приложение по работе с ответственными лицами.
Модели БД описаны в файде ./models.py.

## URL для view-классов

    | URL | View | Метод | Описание | Путь к HTML-шаблону |
    /detail/<pk>/ | ResponsiblePersonDetailView | GET | Получение данных ответственного лица | responsible_person/responsible-person-detail.html

## URL для API

    | URL | ApiView | Метод | Описание |
    /detail/<pk>/ | ResponsiblePersonDetailApiView | GET | Получение деталей ответственного лица
    /create/ | ResponsiblePersonCreateApiView | POST | Создание нового ответственного лица
    /update/<pk>/ | ResponsiblePersonUpdateApiView | PATCH | Частичное обновление ответственного лица
