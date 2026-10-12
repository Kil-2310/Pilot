"""Регистрация ответственного лица: контакт → ФИО → описание."""
import logging

from maxapi import F, Router
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.filters.command import CommandStart
from maxapi.filters.contact import Contact
from maxapi.types import MessageCreated, RequestContactButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.utils.vcf import parse_vcf_info

from services.django_client import DjangoAPIError, get_client

log = logging.getLogger(__name__)

router = Router()


class Registration(StatesGroup):
    """Шаги диалога регистрации."""

    full_name = State()
    description = State()


def _vcf_text(attachment: object) -> str | None:
    """Достать сырую VCF-строку из вложения с контактом.

    Структура Contact-вложения в разных версиях maxapi может отличаться
    (плоское поле vcf_info или payload.vcf_info) — проверяем оба варианта.
    """
    vcf_info = getattr(attachment, "vcf_info", None)
    if vcf_info:
        return vcf_info

    payload = getattr(attachment, "payload", None)
    return getattr(payload, "vcf_info", None) if payload else None


@router.message_created(CommandStart())
async def on_start(event: MessageCreated, context: MemoryContext) -> None:
    """Проверить регистрацию и либо показать приветствие, либо начать регистрацию."""
    from_user = await event.fetch_from_user()
    if from_user is None:
        await event.message.answer("Не удалось определить ваш профиль MAX. Попробуйте ещё раз позже.")
        return

    try:
        existing = await get_client().get_responsible_person(from_user.user_id)
    except DjangoAPIError as exc:
        log.error("Ошибка Django API при проверке регистрации: %s", exc)
        await event.message.answer("Сервер временно недоступен, попробуйте позже.")
        return

    if existing is not None:
        await event.message.answer(
            f"Здравствуйте, {existing['full_name']}! Вы уже зарегистрированы.\n"
            "Команды: /profile, /pilots, /reports"
        )
        return

    builder = InlineKeyboardBuilder()
    builder.row(RequestContactButton(text="Поделиться номером"))
    await event.message.answer(
        "Добро пожаловать в бота проекта «Пилот»!\n\n"
        "Чтобы зарегистрироваться как ответственное лицо, поделитесь, "
        "пожалуйста, номером телефона — он привязан к вашему аккаунту MAX:",
        attachments=[builder.as_markup()],
    )


@router.message_created(Contact())
async def on_contact_received(event: MessageCreated, context: MemoryContext) -> None:
    """Принять контакт, достать телефон и перейти к шагу «ФИО»."""
    attachment = event.message.body.attachments[0]
    vcf_text = _vcf_text(attachment)
    vcf = parse_vcf_info(vcf_text) if vcf_text else None
    phone = vcf.phone if vcf else None

    if not phone:
        await event.message.answer(
            "Не получилось прочитать номер телефона. Попробуйте ещё раз "
            "нажать кнопку «Поделиться номером»."
        )
        return

    from_user = await event.fetch_from_user()
    if from_user is None:
        await event.message.answer("Не удалось определить ваш профиль MAX. Попробуйте ещё раз позже.")
        return

    await context.update_data(
        phone=phone,
        max_user_id=from_user.user_id,
        max_name=from_user.username or from_user.full_name,
    )
    await context.set_state(Registration.full_name)
    await event.message.answer("Телефон получен. Теперь напишите, пожалуйста, ваше ФИО полностью:")


@router.message_created(F.message.body.text, Registration.full_name)
async def on_full_name(event: MessageCreated, context: MemoryContext) -> None:
    """Сохранить ФИО и перейти к шагу «описание»."""
    full_name = event.message.body.text.strip()
    if not full_name:
        await event.message.answer("ФИО не может быть пустым. Введите, пожалуйста, ещё раз:")
        return

    await context.update_data(full_name=full_name)
    await context.set_state(Registration.description)
    await event.message.answer(
        "Коротко расскажите о себе — или отправьте «-», чтобы пропустить:"
    )


@router.message_created(F.message.body.text, Registration.description)
async def on_description(event: MessageCreated, context: MemoryContext) -> None:
    """Сохранить описание и отправить анкету в Django REST API."""
    text = event.message.body.text.strip()
    description = "" if text == "-" else text

    data = await context.get_data()
    request_payload = {
        "full_name": data["full_name"],
        "max_name": data["max_name"],
        "max_user_id": data["max_user_id"],
        "telephone": data["phone"],
        "description": description,
    }

    try:
        await get_client().create_responsible_person(request_payload)
    except DjangoAPIError as exc:
        log.error("Не удалось создать ответственное лицо: %s", exc)
        await context.clear()
        if exc.status_code == 400:
            await event.message.answer(
                "Не получилось зарегистрироваться: возможно, этот телефон или имя в "
                "MAX уже заняты. Отправьте /start, чтобы попробовать ещё раз."
            )
        else:
            await event.message.answer("Сервер временно недоступен, попробуйте позже.")
        return

    await context.clear()
    await event.message.answer(
        "Регистрация завершена, спасибо!\nКоманды: /profile, /pilots, /reports"
    )
