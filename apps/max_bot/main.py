"""Точка входа MAX-бота: запуск через long polling."""
import asyncio
import contextlib
import logging

with contextlib.suppress(ImportError):
    from dotenv import load_dotenv

    load_dotenv()

from bot.dispatcher import build_dispatcher
from bot.ui import get_ui
from config import load_settings
from services.max_api import MaxApiError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("max_bot")

COMMANDS = [
    ("menu", "Главное меню"),
    ("reports", "Отчёты о сопровождаемых"),
    ("pilots", "Найти пилота"),
    ("profile", "Мой профиль"),
]


async def main() -> None:
    settings = load_settings()
    bot, dp = build_dispatcher(settings)
    ui = get_ui()

    try:
        await ui.api.set_commands(COMMANDS)
    except MaxApiError as exc:  # меню команд — удобство, не повод падать
        log.warning("Не удалось зарегистрировать команды бота: %s", exc)

    log.info("Запуск long polling")
    try:
        await dp.start_polling(bot)
    finally:
        await ui.api.aclose()


if __name__ == "__main__":
    asyncio.run(main())
