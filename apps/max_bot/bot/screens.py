"""Построение экранов: запросы к Django + разметка. Роутеры только вызывают build_*."""
from __future__ import annotations

import asyncio
import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from bot.payloads import Nav, PilotsPayload, ProfileEditPayload, RegPayload, ReportPayload
from bot.ui import (
    Screen,
    clip,
    cb,
    contact_button,
    esc,
    link_button,
    menu_button,
)
from config import load_settings
from services.django_client import get_client

PILOTS_PER_PAGE = 5
MAX_PHOTOS = 10   # в schema.yaml лимит вложений не указан — консервативное значение
MAX_VIDEO_BUTTONS = 8
URL_LIMIT = 2048  # LinkButton.url.maxLength

MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
          "сентября", "октября", "ноября", "декабря"]
WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


def _tz() -> ZoneInfo:
    return ZoneInfo(load_settings().timezone)


def today() -> date:
    return datetime.now(_tz()).date()


def fmt_day(day: date) -> str:
    year = f" {day.year}" if day.year != today().year else ""
    return f"{day.day} {MONTHS[day.month - 1]}{year}, {WEEKDAYS[day.weekday()]}"


def _notice(text: str | None) -> str:
    return f"{text}\n\n" if text else ""


# ---------- регистрация ----------

def registration_prompt(notice: str | None = None) -> Screen:
    return Screen(
        f"{_notice(notice)}<b>Добро пожаловать в «Пилот»!</b>\n\n"
        "Чтобы зарегистрироваться как ответственное лицо, поделитесь номером телефона — "
        "он привязан к вашему аккаунту MAX.\n\n<i>Шаг 1 из 3</i>",
        rows=[[contact_button("📱 Поделиться номером")]],
    )


def reg_name_prompt(notice: str | None = None) -> Screen:
    return Screen(
        f"{_notice(notice)}Телефон получен ✅\n\nНапишите ваше <b>ФИО</b> полностью.\n\n<i>Шаг 2 из 3</i>",
        rows=[[cb("Отмена", RegPayload(action="cancel").pack())]],
    )


def reg_description_prompt() -> Screen:
    return Screen(
        "Коротко расскажите о себе (кем приходитесь сопровождаемому и т.п.).\n\n<i>Шаг 3 из 3</i>",
        rows=[[
            cb("Пропустить", RegPayload(action="skip").pack()),
            cb("Отмена", RegPayload(action="cancel").pack()),
        ]],
    )


def reg_done() -> Screen:
    return home_screen("Регистрация завершена, спасибо! ✅")


def reg_failed(conflict: bool) -> Screen:
    if conflict:
        text = ("Не получилось зарегистрироваться: возможно, этот телефон или имя в MAX уже заняты. "
                "Отправьте /start, чтобы попробовать ещё раз.")
    else:
        text = "Сервер временно недоступен, попробуйте позже: отправьте /start."
    return Screen(text)


# ---------- главное меню ----------

def home_screen(notice: str | None = None, name: str | None = None) -> Screen:
    greet = f"Здравствуйте, {esc(name)}!\n" if name else ""
    return Screen(
        f"{_notice(notice)}\n{greet}Что хотите сделать?",
        rows=[
            [cb("📋 Отчёты", Nav(to="reports").pack())],
            [cb("🧑‍✈️ Найти пилота", Nav(to="pilots").pack())],
            [cb("👤 Мой профиль", Nav(to="profile").pack())],
        ],
    )


async def build_home(user_id: int) -> Screen:
    person = await get_client().get_responsible_person(user_id)
    if person is None:
        return registration_prompt()
    return home_screen(name=person.get("full_name"))


# ---------- профиль ----------

async def build_profile(user_id: int, notice: str | None = None) -> Screen:
    person = await get_client().get_responsible_person(user_id)
    if person is None:
        return registration_prompt("Вы пока не зарегистрированы.")
    text = (
        f"{_notice(notice)}<b>Ваш профиль</b>\n\n"
        f"ФИО: {esc(person.get('full_name') or '—')}\n"
        f"Телефон: {esc(person.get('telephone') or '—')}\n"
        f"Имя в MAX: {esc(person.get('max_name') or '—')}\n"
        f"О себе: {esc(clip(person.get('description') or '—', 1000))}"
    )
    return Screen(text, rows=[
        [cb("✏️ ФИО", ProfileEditPayload(field="full_name").pack()),
         cb("✏️ О себе", ProfileEditPayload(field="description").pack())],
        [menu_button()],
    ])


def build_profile_notice_cancelled() -> Screen:
    return Screen(
        "Редактирование отменено.",
        rows=[[cb("👤 Профиль", Nav(to="profile").pack()), menu_button("Меню")]],
    )


def profile_edit_prompt(field: str, notice: str | None = None) -> Screen:
    if field == "full_name":
        ask = "Напишите новое <b>ФИО</b>:"
    else:
        ask = "Напишите новое <b>описание</b> (или нажмите «Очистить»):"
    rows = []
    if field == "description":
        rows.append([cb("Очистить", ProfileEditPayload(field="clear_description").pack())])
    rows.append([cb("Отмена", Nav(to="profile").pack())])
    return Screen(f"{_notice(notice)}{ask}", rows=rows)


# ---------- пилоты ----------

async def build_settlements() -> Screen:
    settlements = await get_client().list_settlements()
    if not settlements:
        return Screen("Сейчас нет доступных населённых пунктов.", rows=[[menu_button()]])
    rows = [[cb(item["name"], PilotsPayload(name=item["name"]).pack())] for item in settlements]
    rows.append([menu_button()])
    return Screen("<b>Пилоты</b>\nВ каком населённом пункте искать?", rows=rows)


async def build_pilots(name: str, page: int = 0) -> Screen:
    pilots = await get_client().list_pilots(name)
    back = [cb("⬅ Населённые пункты", Nav(to="pilots").pack()), menu_button("Меню")]
    if not pilots:
        return Screen(f"В «{esc(name)}» пока нет доступных пилотов.", rows=[back])

    pages = math.ceil(len(pilots) / PILOTS_PER_PAGE)
    page = max(0, min(page, pages - 1))
    chunk = pilots[page * PILOTS_PER_PAGE:(page + 1) * PILOTS_PER_PAGE]

    blocks = []
    for pilot in chunk:
        full_name = f"{pilot.get('first_name', '')} {pilot.get('last_name', '')}".strip()
        block = f"<b>{esc(full_name or 'Без имени')}</b>\n{esc(pilot.get('telephone') or '—')}"
        if pilot.get("description"):
            block += f"\n<i>{esc(clip(pilot['description'], 300))}</i>"
        blocks.append(block)

    header = f"<b>Пилоты в «{esc(name)}»</b>"
    if pages > 1:
        header += f" · стр. {page + 1} из {pages}"

    rows = []
    pager = []
    if page > 0:
        pager.append(cb("◀ Назад", PilotsPayload(name=name, page=page - 1).pack()))
    if page < pages - 1:
        pager.append(cb("Дальше ▶", PilotsPayload(name=name, page=page + 1).pack()))
    if pager:
        rows.append(pager)
    rows.append(back)
    return Screen(header + "\n\n" + "\n\n".join(blocks), rows=rows)


# ---------- сопровождаемые и отчёты ----------

async def build_accompanied(user_id: int) -> Screen:
    client = get_client()
    if await client.get_responsible_person(user_id) is None:
        return registration_prompt("Вы пока не зарегистрированы.")
    people = await client.list_accompanied(user_id)
    if not people:
        return Screen("У вас пока нет привязанных сопровождаемых.", rows=[[menu_button()]])
    day = today().isoformat()
    rows = [
        [cb(p["full_name"], ReportPayload(accompanied_id=p["id"], day=day).pack())]
        for p in people
    ]
    rows.append([menu_button()])
    return Screen("<b>Отчёты</b>\nВыберите сопровождаемого:", rows=rows)


def _note_time(note: dict) -> str:
    try:
        created = datetime.fromisoformat(note["created_at"]).astimezone(_tz())
        return f" · {created:%H:%M}"
    except (KeyError, ValueError, TypeError):
        return ""


async def build_report(user_id: int, accompanied_id: int, day: date, note_idx: int = 0) -> Screen:
    client = get_client()
    people, report = await asyncio.gather(
        client.list_accompanied(user_id), client.get_report(accompanied_id, day.isoformat())
    )
    person = next((p for p in people if p["id"] == accompanied_id), None)
    if person is None:
        return Screen("Этот сопровождаемый не привязан к вам.", rows=[[menu_button()]])

    def pay(d: date, note: int = 0) -> str:
        return ReportPayload(accompanied_id=accompanied_id, day=d.isoformat(), note=note).pack()

    notes = report.get("report_notes") if "report_notes" in report else None
    header = f"<b>{esc(person['full_name'])}</b>\n{fmt_day(day)}"
    images: list[str] = []
    video_rows: list[list[dict]] = []
    note_row: list[dict] = []

    if notes is None:
        body = esc(report.get("message") or "Пилот не создал отчёт в этот день.")
    elif not notes:
        body = "В отчёте за этот день пока нет записей."
    else:
        idx = max(0, min(note_idx, len(notes) - 1))
        note = notes[idx]
        if len(notes) > 1:
            header += f" · запись {idx + 1} из {len(notes)}"
        author = f"{note.get('first_name', '')} {note.get('last_name', '')}".strip() or "пилот"
        lines = [f"<b>{esc(clip(note.get('title') or 'Без названия', 200))}</b>",
                 f"<i>{esc(author)}{_note_time(note)}</i>"]
        if note.get("text"):
            lines += ["", esc(clip(note["text"], 2500))]

        photos = [client.to_absolute_url(p["photo"]) for p in note.get("photos", [])]
        images = photos[:MAX_PHOTOS]
        if len(photos) > MAX_PHOTOS:
            lines += ["", f"<i>Показаны первые {MAX_PHOTOS} фото из {len(photos)}.</i>"]

        for i, video in enumerate(note.get("videos", []), 1):
            url = client.to_absolute_url(video["video"])
            if i <= MAX_VIDEO_BUTTONS and len(url) <= URL_LIMIT:
                video_rows.append([link_button(f"▶ Видео {i}", url)])
            else:
                lines.append(f'<a href="{esc(url)}">Видео {i}</a>')
        body = "\n".join(lines)

        if idx > 0:
            note_row.append(cb("◀ Запись", pay(day, idx - 1)))
        if idx < len(notes) - 1:
            note_row.append(cb("Запись ▶", pay(day, idx + 1)))

    day_row = [cb(f"◀ {day - timedelta(days=1):%d.%m}", pay(day - timedelta(days=1)))]
    if day < today():
        day_row.append(cb(f"{day + timedelta(days=1):%d.%m} ▶", pay(day + timedelta(days=1))))

    rows = video_rows + ([note_row] if note_row else []) + [day_row]
    rows.append([cb("⬅ К списку", Nav(to="reports").pack()), menu_button("Меню")])
    return Screen(f"{header}\n\n{body}", rows=rows, images=images)
