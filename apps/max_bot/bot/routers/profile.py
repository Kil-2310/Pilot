"""Профиль ответственного лица: экран с кнопками «ФИО» / «О себе» (команды /profile, /name, /about сохранены)."""
import logging

from maxapi import F, Router
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.filters.command import Command
from maxapi.types import MessageCallback, MessageCreated

from bot import screens
from bot.payloads import ProfileEditPayload
from bot.ui import Screen, get_ui, server_error_screen
from services.django_client import DjangoAPIError, get_client

log = logging.getLogger(__name__)

router = Router()

NO_PROFILE = "Не удалось определить ваш профиль MAX. Попробуйте ещё раз позже."


class ProfileEdit(StatesGroup):
    """Ожидание нового значения поля профиля."""

    full_name = State()
    description = State()


STATES = {"full_name": ProfileEdit.full_name, "description": ProfileEdit.description}


async def _apply_update(user_id: int, field: str, value: str) -> Screen:
    """PATCH и возврат на экран профиля с пометкой о результате."""
    try:
        await get_client().update_responsible_person(user_id, {field: value})
    except DjangoAPIError as exc:
        log.error("Не удалось обновить профиль: %s", exc)
        if exc.status_code == 400:
            return await screens.build_profile(user_id, "⚠️ Не сохранено: значение не принято сервером.")
        return server_error_screen()
    return await screens.build_profile(user_id, "Сохранено ✅")


@router.message_created(Command("profile"))
async def on_profile_command(event: MessageCreated, context: MemoryContext) -> None:
    await context.clear()
    ui = get_ui()
    from_user = await event.fetch_from_user()
    if from_user is None:
        await ui.show_message(event, Screen(NO_PROFILE))
        return
    ui.typing(event)
    await ui.show_message(event, screens.build_profile(from_user.user_id))


async def _start_edit_by_command(event: MessageCreated, context: MemoryContext, field: str) -> None:
    await context.clear()
    await context.set_state(STATES[field])
    mid = await get_ui().show_message(event, screens.profile_edit_prompt(field))
    if mid:
        await context.update_data(anchor=mid)


@router.message_created(Command("name"))
async def on_name_command(event: MessageCreated, context: MemoryContext) -> None:
    await _start_edit_by_command(event, context, "full_name")


@router.message_created(Command("about"))
async def on_about_command(event: MessageCreated, context: MemoryContext) -> None:
    await _start_edit_by_command(event, context, "description")


@router.message_callback(ProfileEditPayload.filter())
async def on_edit_button(event: MessageCallback, payload: ProfileEditPayload, context: MemoryContext) -> None:
    ui = get_ui()
    user_id = event.callback.user.user_id
    if payload.field == "clear_description":
        await context.clear()
        await ui.show_callback(event, _apply_update(user_id, "description", ""))
        return
    if payload.field not in STATES:
        return
    await context.clear()
    await context.set_state(STATES[payload.field])
    await context.update_data(anchor=event.message.body.mid if event.message else None)
    await ui.show_callback(event, screens.profile_edit_prompt(payload.field))


async def _text_edit(event: MessageCreated, context: MemoryContext, field: str) -> None:
    text = event.message.body.text.strip()
    anchor = (await context.get_data()).get("anchor")
    ui = get_ui()

    if text.startswith("/"):  # команда вместо значения — отменяем, чтобы не сохранить её как значение
        await context.clear()
        await ui.show_message(event, screens.build_profile_notice_cancelled(), anchor)
        return

    if not text:
        await ui.show_message(event, screens.profile_edit_prompt(field, "Значение не может быть пустым."), anchor)
        return

    from_user = await event.fetch_from_user()
    await context.clear()
    if from_user is None:
        await ui.show_message(event, Screen(NO_PROFILE), anchor)
        return
    await ui.show_message(event, _apply_update(from_user.user_id, field, text), anchor)


@router.message_created(F.message.body.text, ProfileEdit.full_name)
async def on_new_full_name(event: MessageCreated, context: MemoryContext) -> None:
    await _text_edit(event, context, "full_name")


@router.message_created(F.message.body.text, ProfileEdit.description)
async def on_new_description(event: MessageCreated, context: MemoryContext) -> None:
    await _text_edit(event, context, "description")
