"""Отчёты: /reports → сопровождаемый → отчёт за сегодня с листанием дней и записей в одном сообщении."""
from datetime import date

from maxapi import Router
from maxapi.context import MemoryContext
from maxapi.filters.command import Command
from maxapi.types import MessageCallback, MessageCreated

from bot import screens
from bot.payloads import ReportPayload
from bot.ui import Screen, get_ui

router = Router()


@router.message_created(Command("reports"))
async def on_reports_command(event: MessageCreated, context: MemoryContext) -> None:
    await context.clear()
    ui = get_ui()
    from_user = await event.fetch_from_user()
    if from_user is None:
        await ui.show_message(event, Screen("Не удалось определить ваш профиль MAX. Попробуйте ещё раз позже."))
        return
    ui.typing(event)
    await ui.show_message(event, screens.build_accompanied(from_user.user_id))


@router.message_callback(ReportPayload.filter())
async def on_report_button(event: MessageCallback, payload: ReportPayload) -> None:
    day = date.fromisoformat(payload.day)
    await get_ui().show_callback(
        event, screens.build_report(event.callback.user.user_id, payload.accompanied_id, day, payload.note)
    )
