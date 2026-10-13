"""Общие хендлеры: старт, главное меню, навигация по кнопкам, /ping."""
from maxapi import Router
from maxapi.context import MemoryContext
from maxapi.filters.command import Command
from maxapi.types import MessageCallback
from maxapi.types.updates.bot_started import BotStarted
from maxapi.types.updates.message_created import MessageCreated

from bot import screens
from bot.payloads import Nav
from bot.ui import Screen, get_ui
from services.django_client import DjangoAPIError

router = Router()

SECTIONS = {
    "home": screens.build_home,
    "profile": screens.build_profile,
    "reports": screens.build_accompanied,
    "pilots": lambda user_id: screens.build_settlements(),
}


@router.bot_started()
async def on_bot_started(event: BotStarted) -> None:
    """Кнопка «Начать»: сразу показываем меню или регистрацию — без «отправьте /start»."""
    ui = get_ui()
    try:
        screen = await screens.build_home(event.user.user_id)
    except DjangoAPIError:
        screen = Screen("Привет! Это бот проекта «Пилот». Сервер временно недоступен — отправьте /start чуть позже.")
    await ui.send(screen, chat_id=event.chat_id)


@router.message_created(Command("menu"))
async def on_menu(event: MessageCreated, context: MemoryContext) -> None:
    await context.clear()
    from_user = await event.fetch_from_user()
    ui = get_ui()
    if from_user is None:
        await ui.show_message(event, Screen("Не удалось определить ваш профиль MAX. Попробуйте позже."))
        return
    ui.typing(event)
    await ui.show_message(event, screens.build_home(from_user.user_id))


@router.message_callback(Nav.filter())
async def on_nav(event: MessageCallback, payload: Nav, context: MemoryContext) -> None:
    await context.clear()  # уход в другой раздел отменяет незаконченный ввод
    build = SECTIONS.get(payload.to, screens.build_home)
    await get_ui().show_callback(event, build(event.callback.user.user_id))


@router.message_created(Command("ping"))
async def on_ping(event: MessageCreated) -> None:
    await event.message.answer("pong")
