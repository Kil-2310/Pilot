"""Тесты логики экранов и Ui. maxapi/httpx в окружении может не быть — подставляем минимальные заглушки.

Запуск: python -m unittest discover -s tests   (из apps/max_bot)
"""
import asyncio
import os
import sys
import types
import unittest
from datetime import date
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("MAX_BOT_TOKEN", "t")
os.environ.setdefault("DJANGO_API_BASE_URL", "http://django:8000/api")

try:  # настоящие библиотеки, если установлены
    import httpx  # noqa: F401
    import maxapi  # noqa: F401
except ImportError:
    httpx = types.ModuleType("httpx")
    httpx.AsyncClient = object
    httpx.AsyncBaseTransport = object
    httpx.Response = object
    httpx.RequestError = type("RequestError", (Exception,), {})
    sys.modules["httpx"] = httpx

    class CallbackPayload:
        def __init_subclass__(cls, prefix="", **kw):
            cls._prefix = prefix

        def __init__(self, **kw):
            for k, v in getattr(type(self), "__annotations__", {}).items():
                setattr(self, k, kw.get(k, getattr(type(self), k, None)))

        def pack(self):
            vals = [str(getattr(self, k)) for k in type(self).__annotations__]
            return "|".join([self._prefix, *vals])

    for name in ("maxapi", "maxapi.filters", "maxapi.filters.callback_payload"):
        sys.modules[name] = types.ModuleType(name)
    sys.modules["maxapi.filters.callback_payload"].CallbackPayload = CallbackPayload

from bot import screens, ui  # noqa: E402
from services.max_api import MaxApiError  # noqa: E402


def run(coro):
    return asyncio.run(coro)


class FakeDjango:
    def __init__(self, notes=None, people=None, pilots=None):
        self.notes, self.pilots = notes, pilots or []
        self.people = people if people is not None else [{"id": 7, "full_name": "Анна <Ивановна>"}]

    async def list_accompanied(self, uid):
        return self.people

    async def get_report(self, aid, day):
        return {"message": "Нет отчёта"} if self.notes is None else {"report_notes": self.notes}

    async def list_pilots(self, name):
        return self.pilots

    def to_absolute_url(self, u):
        return u if u.startswith("http") else "https://site" + u


class ScreensTest(unittest.TestCase):
    def setUp(self):
        screens.today = lambda: date(2026, 10, 13)

    def report(self, notes, day=date(2026, 10, 13), idx=0):
        screens.get_client = lambda: FakeDjango(notes)
        return run(screens.build_report(1, 7, day, idx))

    def test_no_report_keeps_day_navigation_and_escapes_name(self):
        s = self.report(None)
        self.assertIn("Анна &lt;Ивановна&gt;", s.text)
        flat = [b["text"] for r in s.rows for b in r]
        self.assertIn("◀ 12.10", flat)
        self.assertNotIn("14.10 ▶", flat)  # в будущее листать нельзя

    def test_past_day_has_forward_button(self):
        flat = [b["text"] for r in self.report(None, date(2026, 10, 11)).rows for b in r]
        self.assertIn("12.10 ▶", flat)

    def test_note_pages_photos_videos(self):
        notes = [
            {"title": "A", "text": "x", "photos": [{"photo": f"/m/{i}.jpg"} for i in range(12)],
             "videos": [{"video": "/m/v.mp4"}], "created_at": "2026-10-13T09:30:00+00:00"},
            {"title": "B", "text": "y", "photos": [], "videos": []},
        ]
        s = self.report(notes)
        self.assertEqual(len(s.images), screens.MAX_PHOTOS)
        self.assertTrue(s.images[0].startswith("https://site/m/"))
        self.assertIn("запись 1 из 2", s.text)
        self.assertIn("link", [b["type"] for r in s.rows for b in r])
        texts = [b["text"] for r in self.report(notes, idx=1).rows for b in r]
        self.assertIn("◀ Запись", texts)
        self.assertNotIn("Запись ▶", texts)

    def test_foreign_accompanied_rejected(self):
        screens.get_client = lambda: FakeDjango([], people=[])
        self.assertIn("не привязан", run(screens.build_report(1, 7, date(2026, 10, 13))).text)

    def test_text_stays_under_limit(self):
        big = "я" * 10000
        notes = [{"title": big, "text": big, "photos": [], "videos": []}]
        s = self.report(notes)
        self.assertLess(len(ui.render(s)["text"]), ui.TEXT_LIMIT + 1)
        pilots = [{"first_name": big, "last_name": "", "telephone": "1", "description": big}] * 5
        screens.get_client = lambda: FakeDjango(pilots=pilots)
        self.assertLessEqual(len(ui.render(run(screens.build_pilots("Х")))["text"]), ui.TEXT_LIMIT)
        self.assertEqual(ui.fit_text("<b>" + "&amp;" * 2000 + "</b>")[-1], "…")

    def test_pilot_pagination(self):
        pilots = [{"first_name": f"P{i}", "last_name": "", "telephone": "1"} for i in range(11)]
        screens.get_client = lambda: FakeDjango(pilots=pilots)
        s = run(screens.build_pilots("Х", 2))
        self.assertIn("стр. 3 из 3", s.text)
        texts = [b["text"] for r in s.rows for b in r]
        self.assertIn("◀ Назад", texts)
        self.assertNotIn("Дальше ▶", texts)
        self.assertEqual(run(screens.build_pilots("Х", 99)).text.count("<b>P"), 1)  # page зажат


class FakeApi:
    def __init__(self, fail=()):
        self.calls, self.fail = [], list(fail)

    async def _do(self, name, *a):
        self.calls.append((name, *a))
        if self.fail:
            code = self.fail.pop(0)
            if code:
                raise MaxApiError(code, "x")
        return "mid1"

    async def edit_message(self, mid, body):
        return await self._do("edit", mid, body)

    async def send_message(self, body, chat_id=None, user_id=None):
        return await self._do("send", body)

    async def answer_callback(self, cid, body=None, notification=None):
        return await self._do("answer", cid, body, notification)


class UiTest(unittest.TestCase):
    def msg_event(self):
        return NS(message=NS(recipient=NS(chat_id=5, user_id=9)))

    def cb_event(self, message=True):
        return NS(callback=NS(callback_id="c1"), message=NS(recipient=NS(chat_id=5, user_id=9)) if message else None)

    def test_render_always_sends_attachments_list(self):
        self.assertEqual(ui.render(ui.Screen("t"))["attachments"], [])

    def test_edit_anchor_else_send_new(self):
        api = FakeApi(fail=[404])
        mid = run(ui.Ui(api).show_message(self.msg_event(), ui.Screen("t"), anchor="old"))
        self.assertEqual([c[0] for c in api.calls], ["edit", "send"])
        self.assertEqual(mid, "mid1")

    def test_images_fall_back_to_links_on_400(self):
        api = FakeApi(fail=[400])
        run(ui.Ui(api).show_callback(self.cb_event(), ui.Screen("t", images=["https://a/1.jpg"])))
        first, second = api.calls[0][2], api.calls[1][2]
        self.assertTrue(first["attachments"][0]["type"] == "image")
        self.assertEqual(second["attachments"], [])
        self.assertIn("Фото 1", second["text"])

    def test_callback_failure_gives_toast_and_django_error_keeps_screen(self):
        api = FakeApi(fail=[500])
        run(ui.Ui(api).show_callback(self.cb_event(), ui.Screen("t")))
        self.assertEqual(api.calls[-1][3], "Не удалось обновить сообщение, попробуйте ещё раз.")

        from services.django_client import DjangoAPIError

        async def boom():
            raise DjangoAPIError(0, "down")

        api = FakeApi()
        run(ui.Ui(api).show_callback(self.cb_event(), boom()))
        self.assertEqual([c[0] for c in api.calls], ["answer"])
        self.assertIsNone(api.calls[0][2])  # сообщение не заменяли

    def test_deleted_message_gives_toast(self):
        api = FakeApi()
        run(ui.Ui(api).show_callback(self.cb_event(message=False), ui.Screen("t")))
        self.assertIn("устарело", api.calls[0][3])


if __name__ == "__main__":
    unittest.main()
