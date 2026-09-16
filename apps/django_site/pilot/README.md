# App: pilot

## Назначение
Управление пилотом: обновление некоторых данных профиля и получение данных профиля конкретного пилота.
Модели БД описаны в файде ./models.py

## URL

    | URL | View | Метод | Описание | Путь к HTML-шаблону
    '/detail/<pk>' | ProfilePilotDetailView | GET | Получение данных профиля | pilot/pilot-detail.html
    '/update/<pk>' | ProfilePilotUpdateView | GET/POST | Обновление данных профиля | pilot/pilot-update.html
