"""Сопровождаемые и отчёты: /reports → выбор сопровождаемого → выбор даты."""
import logging
from datetime import date, timedelta

from maxapi import Router
from maxapi.filters.callback_payload import CallbackPayload
from maxapi.filters.command import Command
from maxapi.types import CallbackButton, MessageCallback, MessageCreated
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from services.django_client import DjangoAPIError, get_client

log = logging.getLogger(__name__)

router = Router()


class AccompaniedPayload(CallbackPayload, prefix="acc_pick"):
    """Payload кнопки выбора сопровождаемого."""

    id: int


class ReportDatePayload(CallbackPayload, prefix="acc_date"):
    """Payload кнопки выбора даты отчёта."""

    accompanied_id: int
    date: str  # YYYY-MM-DD


@router.message_created(Command("reports"))
async def on_reports_command(event: MessageCreated) -> None:
    """Показать сопровождаемых, привязанных к ответственному лицу."""
    from_user = await event.fetch_from_user()
    if from_user is None:
        await event.message.answer("Не удалось определить ваш профиль MAX. Попробуйте ещё раз позже.")
        return

    client = get_client()

    try:
        responsible = await client.get_responsible_person(from_user.user_id)
    except DjangoAPIError as exc:
        log.error("Ошибка Django API при проверке регистрации: %s", exc)
        await event.message.answer("Сервер временно недоступен, попробуйте позже.")
        return

    if responsible is None:
        await event.message.answer(
            "Вы пока не зарегистрированы. Отправьте /start, чтобы зарегистрироваться."
        )
        return

    try:
        accompanied_list = await client.list_accompanied(from_user.user_id)
    except DjangoAPIError as exc:
        log.error("Ошибка Django API при получении сопровождаемых: %s", exc)
        await event.message.answer("Сервер временно недоступен, попробуйте позже.")
        return

    if not accompanied_list:
        await event.message.answer("У вас пока нет привязанных сопровождаемых.")
        return

    builder = InlineKeyboardBuilder()
    for item in accompanied_list:
        builder.row(
            CallbackButton(text=item["full_name"], payload=AccompaniedPayload(id=item["id"]).pack())
        )

    await event.message.answer("Выберите сопровождаемого:", attachments=[builder.as_markup()])


@router.message_callback(AccompaniedPayload.filter())
async def on_accompanied_chosen(event: MessageCallback, payload: AccompaniedPayload) -> None:
    """Предложить выбрать день отчёта (сегодня/вчера)."""
    today = date.today()
    yesterday = today - timedelta(days=1)

    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(
            text="Сегодня",
            payload=ReportDatePayload(accompanied_id=payload.id, date=today.isoformat()).pack(),
        ),
        CallbackButton(
            text="Вчера",
            payload=ReportDatePayload(
                accompanied_id=payload.id, date=yesterday.isoformat()
            ).pack(),
        ),
    )
    await event.message.answer("За какой день показать отчёт?", attachments=[builder.as_markup()])


@router.message_callback(ReportDatePayload.filter())
async def on_report_date_chosen(event: MessageCallback, payload: ReportDatePayload) -> None:
    """Показать отчёт за выбранную дату (текст заметок + ссылки на фото/видео)."""
    client = get_client()

    try:
        report = await client.get_report(payload.accompanied_id, payload.date)
    except DjangoAPIError as exc:
        log.error("Ошибка Django API при получении отчёта: %s", exc)
        await event.answer(new_text="Сервер временно недоступен, попробуйте позже.")
        return

    if "report_notes" not in report:
        await event.answer(new_text=report.get("message", "Пилот не создал отчёт в этот день."))
        return

    if not report["report_notes"]:
        await event.answer(new_text=f"Отчёт за {payload.date} пуст.")
        return

    lines = [f"Отчёт за {payload.date}:", ""]
    for note in report["report_notes"]:
        author = f"{note.get('first_name', '')} {note.get('last_name', '')}".strip()
        lines.append(f"— {note['title']} ({author or 'пилот'})")
        if note.get("text"):
            lines.append(note["text"])
        for photo in note.get("photos", []):
            lines.append(client.to_absolute_url(photo["photo"]))
        for video in note.get("videos", []):
            lines.append(client.to_absolute_url(video["video"]))
        lines.append("")

    await event.answer(new_text="\n".join(lines).strip())
