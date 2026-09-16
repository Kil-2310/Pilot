# Запуск Django-сайта в режиме разработки

## Настройка проекта

Все команды выполняются в терминале с установленным и активированным виртуальным окружением.

### Перейти в папку с проектом

```bash
cd apps/django_site
```

### Установить зависимости проекта

```bash
pip install -r requirements.txt
```

### Применить миграции

```bash
python manage.py migrate
```

### Загрузить тестовые данные в БД

```bash
python manage.py loaddata site_data.json
```

### Запустить сервер

```bash
python manage.py runserver
```

После запуска сайт будет доступен по адресу: http://127.0.0.1:8000/

## URL сервера и приложения
    
В каждом, приложении присутствует небольшая документация по работе с ним.

    1. /admin/ - админка проекта.
    2. Приложение - authentication. Url - /authentication/. Цель - аутентификация пользователей.
    3. Приложение - pilot. Url - /pilot/. Цель - работа с профилем пилотов.
    4. Приложение - responsible_person. Url - /responsible-person/. Цель - работ с ответственными лицами.
    5. Приложение - accompanied. Url - /accompanied/. Цель - работа с сопровождаемыми.

В режиме разработки, при DEBUG=True, пользователю доступена документация, с описанием API для MAX-бота.

    1. Swagger - /api/schema/swagger
    2. Redoc - /api/schema/redoc/
    3. Схема OpenAPI - /api/schema/

## Пользователи системы

    1. Admin. Username - admin, пароль - 123
    2. Пилот. Username - bob, пароль - 123123Qq
