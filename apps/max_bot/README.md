# Сервис: max_bot

## Назначение

MAX-бот проекта «Пилот». Обслуживает роль ОТВЕТСТВЕННОЕ ЛИЦО: принимает
сообщения из мессенджера MAX и отправляет запросы к Django REST API
(`apps/django_site`).

Реализовано:

- получение сообщений от MAX через long polling (`dp.start_polling`);
- роутинг обработчиков (`Router`/`Dispatcher`);
- FSM-контекст для диалоговых сценариев (в памяти или в Redis);
- асинхронный клиент к Django REST API (`services/django_client.py`);
- регистрация ответственного лица (`bot/routers/registration.py`):
  `/start` → проверка, зарегистрирован ли пользователь
  (`GET /responsible-person/detail/<max_user_id>/`) → если нет, запрос
  телефона кнопкой `request_contact` → ФИО → статус (кнопки) →
  описание → `POST /responsible-person/create/`.

Ещё не реализовано: просмотр пилотов с фильтром по населённому пункту,
список сопровождаемых и отчёты, обновление анкеты (`PATCH`) — всё это
на основе уже существующих эндпоинтов `apps/django_site` (`pilot`,
`accompanied`, `report`).

**Не проверено на реальном боте.** `Contact`-вложение (номер телефона
из кнопки `request_contact`) в коде ищется и как `attachment.vcf_info`,
и как `attachment.payload.vcf_info` — на момент написания в
автогенерированной документации `maxapi` точная структура этого поля
не отображалась. Если при реальном тесте телефон не распознаётся —
смотрите `bot/routers/registration.py`, функцию `_vcf_text`, и
проверьте там актуальную структуру вложения.

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
