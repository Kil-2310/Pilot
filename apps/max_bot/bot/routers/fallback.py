"""Подключается последним: ловит то, что не обработали остальные роутеры."""
from maxapi import Router
from maxapi.context import MemoryContext
from maxapi.types import MessageCallback, MessageCreated

from bot import screens
from bot.payloads import PREFIXES
from bot.ui import get_ui

router = Router()


@router.message_callback()
async def on_stale_button(event: MessageCallback) -> None:
    """Кнопка из старого сообщения (после обновления бота): превращаем сообщение в меню."""
    payload = event.callback.payload or ""
    if payload.startswith(PREFIXES):
        return  # известная кнопка — её обработает свой роутер
    await get_ui().show_callback(event, screens.build_home(event.callback.user.user_id))


@router.message_created()
async def on_unknown_message(event: MessageCreated, context: MemoryContext) -> None:
    """Произвольный текст вне диалога: вместо молчания показываем меню."""
    text = (event.message.body.text or "") if event.message.body else ""
    if not text or text.startswith("/") or await context.get_state():
        return
    from_user = await event.fetch_from_user()
    if from_user is not None:
        await get_ui().show_message(event, screens.build_home(from_user.user_id))
