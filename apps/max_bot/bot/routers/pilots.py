"""Просмотр пилотов с фильтром по населённому пункту: /pilots."""
import logging

from maxapi import Router
from maxapi.filters.callback_payload import CallbackPayload
from maxapi.filters.command import Command
from maxapi.types import CallbackButton, MessageCallback, MessageCreated
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from services.django_client import DjangoAPIError, get_client

log = logging.getLogger(__name__)

router = Router()


class SettlementPayload(CallbackPayload, prefix="pilots_settlement"):
    """Payload кнопки выбора населённого пункта."""

    name: str


@router.message_created(Command("pilots"))
async def on_pilots_command(event: MessageCreated) -> None:
    """Показать кнопки с населёнными пунктами, где работают пилоты."""
    try:
        settlements = await get_client().list_settlements()
    except DjangoAPIError as exc:
        log.error("Ошибка Django API при получении населённых пунктов: %s", exc)
        await event.message.answer("Сервер временно недоступен, попробуйте позже.")
        return

    if not settlements:
        await event.message.answer("Сейчас нет доступных населённых пунктов.")
        return

    builder = InlineKeyboardBuilder()
    for item in settlements:
        builder.row(
            CallbackButton(text=item["name"], payload=SettlementPayload(name=item["name"]).pack())
        )

    await event.message.answer(
        "В каком населённом пункте искать пилотов?",
        attachments=[builder.as_markup()],
    )


@router.message_callback(SettlementPayload.filter())
async def on_settlement_chosen(event: MessageCallback, payload: SettlementPayload) -> None:
    """Показать пилотов, работающих в выбранном населённом пункте."""
    try:
        pilots = await get_client().list_pilots(payload.name)
    except DjangoAPIError as exc:
        log.error("Ошибка Django API при получении пилотов: %s", exc)
        await event.answer(new_text="Сервер временно недоступен, попробуйте позже.")
        return

    if not pilots:
        await event.answer(new_text=f"В «{payload.name}» пока нет доступных пилотов.")
        return

    lines = [f"Пилоты в «{payload.name}»:", ""]
    for pilot in pilots:
        full_name = f"{pilot.get('first_name', '')} {pilot.get('last_name', '')}".strip()
        lines.append(f"• {full_name or 'Без имени'}, тел. {pilot.get('telephone', '—')}")
        if pilot.get("description"):
            lines.append(f"  {pilot['description']}")

    await event.answer(new_text="\n".join(lines))
