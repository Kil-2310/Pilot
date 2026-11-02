"""Тонкий клиент к MAX Bot API (см. schema.yaml) для операций, которых нет в удобном виде в хендлерах:

- редактирование сообщения (PUT /messages) — чтобы не плодить новые;
- ответ на нажатие кнопки с заменой сообщения (POST /answers);
- «печатает…» (POST /chats/{id}/actions);
- меню команд бота (PATCH /me/commands).

Приём событий по-прежнему делает maxapi; здесь только исходящие вызовы.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)


class MaxApiError(Exception):
    """MAX API ответил ошибкой (status >= 400) или недоступен (status == 0)."""

    def __init__(self, status_code: int, detail: Any) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"MAX API вернул {status_code}: {detail!r}")


class MaxApiClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://platform-api2.max.ru",
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": token},
            timeout=timeout,
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def send_message(
        self, body: dict, chat_id: int | None = None, user_id: int | None = None
    ) -> str | None:
        """Отправить сообщение в чат (или пользователю), вернуть его id (mid)."""
        params = {"chat_id": chat_id} if chat_id is not None else {"user_id": user_id}
        data = await self._request("POST", "/messages", params=params, json=body)
        return ((data or {}).get("message") or {}).get("body", {}).get("mid")

    async def edit_message(self, message_id: str, body: dict) -> None:
        """Заменить текст/вложения сообщения.

        Важно: attachments=None оставляет вложения как были, [] — удаляет все
        (в т.ч. клавиатуру), поэтому клавиатуру передаём всегда явно.
        """
        await self._request("PUT", "/messages", params={"message_id": message_id}, json=body)

    async def answer_callback(
        self, callback_id: str, body: dict | None = None, notification: str | None = None
    ) -> None:
        """Ответить на нажатие кнопки: заменить сообщение и/или показать всплывающее уведомление."""
        payload: dict[str, Any] = {}
        if body is not None:
            payload["message"] = body
        if notification:
            payload["notification"] = notification
        await self._request("POST", "/answers", params={"callback_id": callback_id}, json=payload)

    async def send_action(self, chat_id: int, action: str = "typing_on") -> None:
        """Показать собеседнику индикатор действия («печатает…»). Ошибки не критичны."""
        try:
            await self._request("POST", f"/chats/{chat_id}/actions", json={"action": action})
        except MaxApiError as exc:
            log.debug("send_action не удался: %s", exc)

    async def set_commands(self, commands: list[tuple[str, str]]) -> None:
        """Зарегистрировать команды в меню «/» (до 32 штук, описание до 128 символов)."""
        body = {"commands": [{"name": n, "description": d[:128]} for n, d in commands]}
        await self._request("PATCH", "/me/commands", json=body)

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = await self._client.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            raise MaxApiError(0, str(exc)) from exc
        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            raise MaxApiError(response.status_code, detail)
        try:
            return response.json()
        except ValueError:
            return None
