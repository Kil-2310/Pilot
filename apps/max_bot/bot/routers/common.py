"""Общие хендлеры бота: приветствие, /start, /ping."""
from maxapi import Router
from maxapi.filters.command import Command, CommandStart
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


@router.message_created(CommandStart())
async def on_start(event: MessageCreated) -> None:
    """Обработка команды /start."""
    await event.message.answer(
        "Бот проекта «Пилот» запущен.\n"
        "Основной функционал (регистрация ответственного лица, список "
        "пилотов, отчёты) будет добавлен отдельно."
    )


@router.message_created(Command("ping"))
async def on_ping(event: MessageCreated) -> None:
    """Проверка, что бот отвечает."""
    await event.message.answer("pong")
