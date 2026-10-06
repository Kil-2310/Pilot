"""Конфигурация MAX-бота, считывается из переменных окружения."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    django_api_base_url: str
    redis_url: str | None


def load_settings() -> Settings:
    """Собрать настройки из переменных окружения (см. README.md)."""
    return Settings(
        bot_token=os.environ["MAX_BOT_TOKEN"],
        django_api_base_url=os.environ["DJANGO_API_BASE_URL"],
        redis_url=os.getenv("REDIS_URL") or None,
    )
