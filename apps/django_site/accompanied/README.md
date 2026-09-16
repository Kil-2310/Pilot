# App: accompanied

## Назначение
Приложение предназнечено для получения списка, деталей, создание, обновлениея, удаления сопровождаемых.
Модели БД описаны в файде ./models.py

## URL

    | URL | View | Метод | Описание | Путь к HTML-шаблону
    '/' | AccompaniedListView | GET | Получение ввсех сопровождаемых | accompanied/accompanied-list.html
    'detail/<pk>/' | AccompaniedDetailView | GET | Получение деталей сопровождаемого | accompanied/accompanied-detail.html
    'create/<pk>/' | AccompaniedCreateView | POST | Создание нового сопровождаемого | accompanied/accompanied-create.html
    'update/<pk>' | AccompaniedUpdateView | GET/POST | Обновление сопровождаемого | accompanied/accompanied-update.html
    'delete/<pk>' | AccompaniedDeleteView | POST | Отвязка пилота от сопровождаемого (без удаления сопровождаемого) | accompanied/accompanied-delete.html