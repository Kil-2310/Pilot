"""Асинхронный клиент к Django REST API (apps/django_site) для вызовов из бота."""
from __future__ import annotations

from typing import Any

import httpx

from config import load_settings


class DjangoAPIError(Exception):
    """Django REST API ответил ошибкой (status >= 400) или недоступен (status == 0)."""

    def __init__(self, status_code: int, detail: Any) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Django API вернул {status_code}: {detail!r}")


class DjangoAPIClient:
    """Тонкая обёртка над эндпоинтами responsible_person и pilot."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def get_responsible_person(self, max_user_id: int) -> dict | None:
        """Вернуть ответственное лицо по max_user_id или None, если его ещё нет."""
        response = await self._request("GET", f"/responsible-person/detail/{max_user_id}/")
        if response.status_code == 404:
            return None
        self._raise_for_error(response)
        return response.json()

    async def create_responsible_person(self, data: dict) -> dict:
        """Зарегистрировать новое ответственное лицо."""
        response = await self._request("POST", "/responsible-person/create/", json=data)
        self._raise_for_error(response)
        return response.json()

    async def list_settlements(self) -> list[dict]:
        """Список населённых пунктов, в которых работают пилоты."""
        response = await self._request("GET", "/pilot/settlement/")
        self._raise_for_error(response)
        return self._unwrap_list(response.json())

    async def list_pilots(self, settlement_name: str) -> list[dict]:
        """Пилоты, работающие в указанном населённом пункте."""
        response = await self._request(
            "GET", "/pilot/", params={"settlements__name": settlement_name}
        )
        self._raise_for_error(response)
        return self._unwrap_list(response.json())

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
                return await client.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            raise DjangoAPIError(0, str(exc)) from exc

    @staticmethod
    def _unwrap_list(data: Any) -> list[dict]:
        """DRF с пагинацией отдаёт {"results": [...]}, без пагинации — просто список."""
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    @staticmethod
    def _raise_for_error(response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise DjangoAPIError(response.status_code, detail)


_client: DjangoAPIClient | None = None


def get_client() -> DjangoAPIClient:
    """Вернуть единый на процесс экземпляр клиента (создаётся при первом обращении)."""
    global _client
    if _client is None:
        _client = DjangoAPIClient(load_settings().django_api_base_url)
    return _client
