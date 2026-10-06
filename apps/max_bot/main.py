"""Точка входа MAX-бота: запуск через long polling."""
import asyncio
import contextlib
import logging

with contextlib.suppress(ImportError):
    from dotenv import load_dotenv

    load_dotenv()

from bot.dispatcher import build_dispatcher
from config import load_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("max_bot")


async def main() -> None:
    settings = load_settings()
    bot, dp = build_dispatcher(settings)

    log.info("Запуск long polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
