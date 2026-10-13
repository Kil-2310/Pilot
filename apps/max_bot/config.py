"""Конфигурация MAX-бота, считывается из переменных окружения."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    django_api_base_url: str
    redis_url: str | None
    max_api_base_url: str
    timezone: str


def load_settings() -> Settings:
    """Собрать настройки из переменных окружения (см. README.md)."""
    return Settings(
        bot_token=os.environ["MAX_BOT_TOKEN"],
        django_api_base_url=os.environ["DJANGO_API_BASE_URL"],
        redis_url=os.getenv("REDIS_URL") or None,
        # Базовый адрес Bot API взят из schema.yaml; переопределяется при необходимости.
        max_api_base_url=os.getenv("MAX_API_BASE_URL", "https://platform-api2.max.ru"),
        # Нужен, чтобы «сегодня/вчера» в отчётах считались по местному времени,
        # а не по UTC контейнера.
        timezone=os.getenv("BOT_TIMEZONE", "Europe/Moscow"),
    )
