"""«Экраны» MAX-бота: одно сообщение, которое редактируется, а не плодит новые.

Экран (`Screen`) = HTML-текст + ряды кнопок + картинки по URL. `Ui` умеет:
- заменить сообщение в ответ на нажатие кнопки (POST /answers);
- отредактировать «якорное» сообщение бота после текстового ввода пользователя
  (PUT /messages), а если его нет или оно недоступно — отправить новое.
"""
from __future__ import annotations

import asyncio
import html
import inspect
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

from bot.payloads import Nav
from config import load_settings
from services.django_client import DjangoAPIError
from services.max_api import MaxApiClient, MaxApiError

log = logging.getLogger(__name__)

TEXT_LIMIT = 4000  # NewMessageBody.text.maxLength


def esc(value: Any) -> str:
    """Экранировать пользовательский текст для format=html."""
    return html.escape(str(value), quote=False)


def clip(value: Any, limit: int) -> str:
    """Обрезать пользовательский текст (до экранирования), чтобы не упереться в лимит 4000."""
    text = str(value).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def cb(text: str, payload: str) -> dict:
    return {"type": "callback", "text": text, "payload": payload}


def link_button(text: str, url: str) -> dict:
    return {"type": "link", "text": text, "url": url}


def contact_button(text: str) -> dict:
    return {"type": "request_contact", "text": text}


def menu_button(text: str = "⬅ Меню") -> dict:
    return cb(text, Nav(to="home").pack())


@dataclass
class Screen:
    text: str
    rows: list[list[dict]] = field(default_factory=list)
    images: list[str] = field(default_factory=list)

    def without_images(self) -> "Screen":
        """Вариант без картинок: ссылки на фото уходят в текст (запасной путь)."""
        links = "\n".join(
            f'<a href="{esc(url)}">Фото {i}</a>' for i, url in enumerate(self.images, 1)
        )
        text = f"{self.text}\n\n{links}" if links else self.text
        return Screen(text=text, rows=self.rows, images=[])


def fit_text(text: str) -> str:
    """Предохранитель от лимита 4000: при переполнении убираем теги и режем, не ломая HTML-сущность."""
    if len(text) <= TEXT_LIMIT:
        return text
    plain = re.sub(r"<[^>]+>", "", text)[: TEXT_LIMIT - 1]
    amp = plain.rfind("&")
    if amp != -1 and ";" not in plain[amp:]:
        plain = plain[:amp]
    return plain.rstrip() + "…"


def render(screen: Screen) -> dict:
    """Screen → NewMessageBody (см. schema.yaml). attachments всегда список: [] убирает старую клавиатуру."""
    attachments: list[dict] = [{"type": "image", "payload": {"url": u}} for u in screen.images]
    if screen.rows:
        attachments.append({"type": "inline_keyboard", "payload": {"buttons": screen.rows}})
    return {"text": fit_text(screen.text), "format": "html", "attachments": attachments}


def server_error_screen() -> Screen:
    return Screen(
        "Сервер временно недоступен, попробуйте чуть позже.",
        rows=[[menu_button("⬅ В меню")]],
    )


def _target(event: Any) -> tuple[int | None, int | None]:
    recipient = event.message.recipient
    return recipient.chat_id, recipient.user_id


class Ui:
    def __init__(self, api: MaxApiClient) -> None:
        self.api = api

    async def send(
        self, screen: Screen, chat_id: int | None = None, user_id: int | None = None
    ) -> str | None:
        return await self._deliver(lambda body: self.api.send_message(body, chat_id, user_id), screen)

    async def place(
        self,
        screen: Screen,
        chat_id: int | None,
        user_id: int | None,
        anchor: str | None,
    ) -> str | None:
        """Показать экран: отредактировать anchor, а если нельзя — отправить новое сообщение."""
        if anchor:
            try:
                await self._deliver(lambda body: self.api.edit_message(anchor, body), screen)
                return anchor
            except MaxApiError as exc:
                log.info("Якорное сообщение %s не отредактировать (%s), отправляю новое", anchor, exc)
        return await self.send(screen, chat_id, user_id)

    async def show_message(
        self, event: Any, build: Screen | Awaitable[Screen], anchor: str | None = None
    ) -> str | None:
        """Ответ на сообщение/команду пользователя. Возвращает id показанного сообщения."""
        try:
            screen = await build if inspect.isawaitable(build) else build
        except DjangoAPIError as exc:
            log.error("Ошибка Django API: %s", exc)
            screen = server_error_screen()
        chat_id, user_id = _target(event)
        return await self.place(screen, chat_id, user_id, anchor)

    async def show_callback(self, event: Any, build: Screen | Awaitable[Screen]) -> None:
        """Ответ на нажатие кнопки: заменить текущее сообщение (или показать всплывающую подсказку)."""
        callback_id = event.callback.callback_id
        try:
            screen = await build if inspect.isawaitable(build) else build
        except DjangoAPIError as exc:
            # Остаёмся на текущем экране — человек может просто нажать кнопку ещё раз.
            log.error("Ошибка Django API: %s", exc)
            await self._toast(callback_id, "Сервер временно недоступен, попробуйте позже.")
            return

        if event.message is None:
            await self._toast(callback_id, "Сообщение устарело. Отправьте /menu.")
            return

        try:
            await self._deliver(lambda body: self.api.answer_callback(callback_id, body), screen)
        except MaxApiError as exc:
            log.error("Не удалось заменить сообщение по кнопке: %s", exc)
            await self._toast(callback_id, "Не удалось обновить сообщение, попробуйте ещё раз.")

    def typing(self, event: Any) -> None:
        """Показать «печатает…», пока бот ходит в Django (не блокирует обработку)."""
        chat_id, _ = _target(event)
        if chat_id is not None:
            asyncio.create_task(self.api.send_action(chat_id, "typing_on"))

    async def _toast(self, callback_id: str, text: str) -> None:
        try:
            await self.api.answer_callback(callback_id, notification=text)
        except MaxApiError as exc:
            log.warning("Не удалось ответить на callback: %s", exc)

    async def _deliver(self, op: Callable[[dict], Awaitable[Any]], screen: Screen) -> Any:
        try:
            return await op(render(screen))
        except MaxApiError as exc:
            # Картинку по URL MAX не смог принять (недоступный адрес и т.п.) — показываем ссылками.
            if screen.images and exc.status_code == 400:
                log.warning("MAX не принял картинки (%s), показываю ссылками", exc)
                return await op(render(screen.without_images()))
            raise


_ui: Ui | None = None


def get_ui() -> Ui:
    """Единый на процесс экземпляр (создаётся при первом обращении)."""
    global _ui
    if _ui is None:
        settings = load_settings()
        _ui = Ui(MaxApiClient(settings.bot_token, settings.max_api_base_url))
    return _ui
