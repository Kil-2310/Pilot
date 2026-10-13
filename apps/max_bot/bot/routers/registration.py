"""Регистрация ответственного лица: контакт → ФИО → описание. Всё в одном редактируемом сообщении."""
import logging

from maxapi import F, Router
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.filters.command import CommandStart
from maxapi.filters.contact import Contact
from maxapi.types import MessageCallback, MessageCreated
from maxapi.utils.vcf import parse_vcf_info

from bot import screens
from bot.payloads import RegPayload
from bot.ui import Screen, get_ui
from services.django_client import DjangoAPIError, get_client

log = logging.getLogger(__name__)

router = Router()

NO_PROFILE = "Не удалось определить ваш профиль MAX. Попробуйте ещё раз позже."


class Registration(StatesGroup):
    """Шаги диалога регистрации."""

    full_name = State()
    description = State()


def _vcf_text(attachment: object) -> str | None:
    """Сырая VCF-строка из вложения с контактом (плоское поле или payload.vcf_info)."""
    vcf_info = getattr(attachment, "vcf_info", None)
    if vcf_info:
        return vcf_info
    payload = getattr(attachment, "payload", None)
    return getattr(payload, "vcf_info", None) if payload else None


async def _anchor(context: MemoryContext) -> str | None:
    return (await context.get_data()).get("anchor")


async def _show(event, context: MemoryContext, screen: Screen) -> None:
    """Показать экран в якорном сообщении и запомнить его id."""
    mid = await get_ui().show_message(event, screen, await _anchor(context))
    if mid:
        await context.update_data(anchor=mid)


@router.message_created(CommandStart())
async def on_start(event: MessageCreated, context: MemoryContext) -> None:
    await context.clear()
    ui = get_ui()
    from_user = await event.fetch_from_user()
    if from_user is None:
        await ui.show_message(event, Screen(NO_PROFILE))
        return
    ui.typing(event)
    mid = await ui.show_message(event, screens.build_home(from_user.user_id))
    if mid:
        await context.update_data(anchor=mid)


@router.message_created(Contact())
async def on_contact_received(event: MessageCreated, context: MemoryContext) -> None:
    attachment = event.message.body.attachments[0]
    vcf_text = _vcf_text(attachment)
    vcf = parse_vcf_info(vcf_text) if vcf_text else None
    phone = vcf.phone if vcf else None

    if not phone:
        await _show(event, context, screens.registration_prompt(
            "Не получилось прочитать номер. Нажмите «Поделиться номером» ещё раз."))
        return

    from_user = await event.fetch_from_user()
    if from_user is None:
        await get_ui().show_message(event, Screen(NO_PROFILE))
        return

    await context.update_data(
        phone=phone,
        max_user_id=from_user.user_id,
        max_name=from_user.username or from_user.full_name,
    )
    await context.set_state(Registration.full_name)
    await _show(event, context, screens.reg_name_prompt())


@router.message_created(F.message.body.text, Registration.full_name)
async def on_full_name(event: MessageCreated, context: MemoryContext) -> None:
    full_name = event.message.body.text.strip()
    if not full_name or full_name.startswith("/"):
        await _show(event, context, screens.reg_name_prompt("Введите ФИО текстом, не командой."))
        return
    await context.update_data(full_name=full_name)
    await context.set_state(Registration.description)
    await _show(event, context, screens.reg_description_prompt())


async def _submit(context: MemoryContext, description: str) -> Screen:
    """Отправить анкету в Django; всегда возвращает экран (ошибки обработаны внутри)."""
    data = await context.get_data()
    if not all(k in data for k in ("full_name", "max_user_id", "phone")):
        await context.clear()
        return screens.registration_prompt("Сессия регистрации устарела — начните заново.")

    payload = {
        "full_name": data["full_name"],
        "max_name": data.get("max_name"),
        "max_user_id": data["max_user_id"],
        "telephone": data["phone"],
        "description": description,
    }
    try:
        await get_client().create_responsible_person(payload)
    except DjangoAPIError as exc:
        log.error("Не удалось создать ответственное лицо: %s", exc)
        await context.clear()
        return screens.reg_failed(conflict=exc.status_code == 400)
    await context.clear()
    return screens.reg_done()


@router.message_created(F.message.body.text, Registration.description)
async def on_description(event: MessageCreated, context: MemoryContext) -> None:
    text = event.message.body.text.strip()
    anchor = await _anchor(context)
    screen = await _submit(context, "" if text == "-" else text)
    await get_ui().show_message(event, screen, anchor)


@router.message_callback(RegPayload.filter())
async def on_reg_button(event: MessageCallback, payload: RegPayload, context: MemoryContext) -> None:
    ui = get_ui()
    if payload.action == "skip":
        await ui.show_callback(event, _submit(context, ""))
    else:  # cancel
        await context.clear()
        await ui.show_callback(event, screens.build_home(event.callback.user.user_id))
