# App: report

## Назначение
Приложение по работе с отчетами.
Модели БД описаны в файде ./models.py.

## URL

    | URL | View | Метод | Описание | Путь к HTML-шаблону |
    /accompanied/<int:accompanied_pk>/ | ReportListByAccompaniedView | GET | Создание ежедневного отчета и получение списка из последних 3 отчетов | report/report-list.html
    /detail/<int:pk>/ | ReportDetailView | GET | Получение деталей отчета | report/report-detail.html
    /detail/<int:pk>/note/create/ | ReportNoteCreateView | POST | Создание заметки | report/report-note-create.html

## Url для API
    
    | URL | ApiView | Метод | Описание |
    /accompanied-detail/<accompanied_id>/<date>/ | ReportDetailByDateView | GET | Получение отчета по дате и id сопровождаемого
