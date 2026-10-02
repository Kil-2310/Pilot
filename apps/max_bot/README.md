# Сервис: max_bot

## Назначение

MAX-бот проекта «Пилот». Обслуживает роль ОТВЕТСТВЕННОЕ ЛИЦО: принимает
сообщения из мессенджера MAX и отправляет запросы к Django REST API
(`apps/django_site`).

На данном этапе реализован только каркас:

- получение сообщений от MAX через long polling (`dp.start_polling`);
- роутинг обработчиков (`Router`/`Dispatcher`);
- FSM-контекст для диалоговых сценариев (в памяти или в Redis).

Бизнес-логика (регистрация ответственного лица, просмотр пилотов с
фильтром по населённому пункту, получение отчётов) и клиент к Django
REST API будут добавлены отдельно, на основе уже существующих
эндпоинтов `apps/django_site` (`responsible_person`, `pilot`,
`accompanied`, `report`).

## Стек

Python 3.12, [maxapi](https://github.com/love-apples/maxapi) (обёртка над
MAX Bot API в стиле aiogram), Redis (хранилище FSM, опционально).

## Переменные окружения

    | Переменная | Обязательна | Описание |
    MAX_BOT_TOKEN | да | Токен бота, выданный при создании бота в MAX |
    DJANGO_API_BASE_URL | да | Базовый URL Django REST API, например http://django_app:8000/api |
    REDIS_URL | нет | URL Redis для хранения FSM, например redis://redis:6379/0. Если не задан — состояния хранятся в памяти процесса и теряются при перезапуске |

## Про long polling

Бот сам постоянно спрашивает MAX API, нет ли новых событий — поэтому не
нужен домен, HTTPS-сертификат и открытый порт. Это удобно для разработки
и небольшой нагрузки, но у long polling есть официальное предупреждение:
он ограничен по скорости и сроку хранения событий и **не рекомендуется
для production**. Для боевого окружения библиотека `maxapi` поддерживает
переключение на webhook (через aiohttp/FastAPI/Litestar) — дайте знать,
когда это понадобится, вернуть вебхук — дело нескольких строк в `main.py`.

Если у бота ранее были активные webhook-подписки, события не будут
приходить через polling, пока подписки не снять — `await bot.delete_webhook()`.

## Структура

    main.py                — точка входа: запуск long polling
    config.py               — конфигурация из переменных окружения
    bot/dispatcher.py       — сборка Bot/Dispatcher, подключение хранилища FSM
    bot/routers/common.py   — общие хендлеры (/start, /ping, приветствие)

## Локальный запуск (без Docker)

    pip install -r requirements.txt
    MAX_BOT_TOKEN=... DJANGO_API_BASE_URL=http://localhost:8000/api python main.py
