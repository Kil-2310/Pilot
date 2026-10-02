"""Общие хендлеры бота: приветствие при запуске и /ping."""
from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types.updates.bot_started import BotStarted
from maxapi.types.updates.message_created import MessageCreated

router = Router()


@router.bot_started()
async def on_bot_started(event: BotStarted) -> None:
    """Приветствие при первом запуске бота пользователем (кнопка «Начать»)."""
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Привет! Это бот проекта «Пилот». Отправьте /start, чтобы начать.",
    )


@router.message_created(Command("ping"))
async def on_ping(event: MessageCreated) -> None:
    """Проверка, что бот отвечает."""
    await event.message.answer("pong")
