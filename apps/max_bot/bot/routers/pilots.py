"""Просмотр пилотов по населённым пунктам: /pilots и кнопки (страницы листаются в том же сообщении)."""
from maxapi import Router
from maxapi.context import MemoryContext
from maxapi.filters.command import Command
from maxapi.types import MessageCallback, MessageCreated

from bot import screens
from bot.payloads import PilotsPayload
from bot.ui import get_ui

router = Router()


@router.message_created(Command("pilots"))
async def on_pilots_command(event: MessageCreated, context: MemoryContext) -> None:
    await context.clear()
    ui = get_ui()
    ui.typing(event)
    await ui.show_message(event, screens.build_settlements())


@router.message_callback(PilotsPayload.filter())
async def on_pilots_button(event: MessageCallback, payload: PilotsPayload) -> None:
    await get_ui().show_callback(event, screens.build_pilots(payload.name, payload.page))
