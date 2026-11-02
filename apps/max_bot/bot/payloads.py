"""Payload'ы inline-кнопок. У каждого уникальный префикс — он же используется в fallback-роутере."""
from maxapi.filters.callback_payload import CallbackPayload


class Nav(CallbackPayload, prefix="m_nav"):
    """Переход в раздел: home / profile / pilots / reports."""

    to: str


class RegPayload(CallbackPayload, prefix="m_reg"):
    """Кнопки внутри регистрации: skip / cancel."""

    action: str


class ProfileEditPayload(CallbackPayload, prefix="m_pf"):
    """Начать редактирование поля профиля: full_name / description."""

    field: str


class PilotsPayload(CallbackPayload, prefix="m_pil"):
    """Пилоты выбранного населённого пункта, страница page (с 0)."""

    name: str
    page: int = 0


class ReportPayload(CallbackPayload, prefix="m_rep"):
    """Отчёт сопровождаемого за день (YYYY-MM-DD), запись note (с 0)."""

    accompanied_id: int
    day: str
    note: int = 0


PREFIXES = ("m_nav", "m_reg", "m_pf", "m_pil", "m_rep")
