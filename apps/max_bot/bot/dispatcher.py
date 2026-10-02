"""Инициализация Bot и Dispatcher, подключение роутеров и хранилища FSM."""
import logging

from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext

from bot.routers.common import router as common_router
from bot.routers.registration import router as registration_router
from config import Settings

log = logging.getLogger(__name__)


def build_dispatcher(settings: Settings) -> tuple[Bot, Dispatcher]:
    """Собрать Bot и Dispatcher согласно конфигурации.

    Если задан REDIS_URL — состояния FSM хранятся в Redis (переживают
    перезапуск бота). Иначе — в памяти процесса (MemoryContext).
    """
    bot = Bot(settings.bot_token)

    if settings.redis_url:
        import redis.asyncio as redis
        from maxapi.context import RedisContext

        redis_client = redis.Redis.from_url(settings.redis_url)
        dp = Dispatcher(
            storage=RedisContext,
            redis_client=redis_client,
            key_prefix="pilot_max_bot",
        )
        log.info("FSM-хранилище: Redis (%s)", settings.redis_url)
    else:
        dp = Dispatcher(storage=MemoryContext)
        log.info("FSM-хранилище: память процесса (REDIS_URL не задан)")

    dp.include_routers(common_router, registration_router)

    return bot, dp
