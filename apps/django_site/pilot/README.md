# App: pilot

## Назначение
Приложение по работе с пилотами.
Модели БД описаны в файде ./models.py.

## URL

    | URL | View | Метод | Описание | Путь к HTML-шаблону |
    /detail/<pk>/ | ProfilePilotDetailView | GET | Получение данных профиля | pilot/pilot-detail.html
    /update/<pk>/ | ProfilePilotUpdateView | GET/POST | Обновление данных профиля | pilot/pilot-update.html

## URL для API

    | URL | ApiView | Метод | Описание |
    / | ProfilePilotListAPIView | GET | Получение всех пилотов с фильтрацией по населенному пункту
    /detail/<pk>/ | ProfilePilotRetrieveAPIView | GET | Получение деталей конкретного пилота
    /settlement/ | SettlementListAPIView | GET | Получение всех доступных населенных пунктов, в которых работают пилоты
