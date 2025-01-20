from aiogram import Dispatcher
from .start import register_handlers_start
from .competition import register_handlers_competition
from .leaderboard import register_handlers_leaderboard
from .common import register_handlers_common

def register_handlers(dp: Dispatcher):
    # Сначала регистрируем общие обработчики
    register_handlers_common(dp)
    # Затем остальные
    register_handlers_start(dp)
    register_handlers_competition(dp)
    register_handlers_leaderboard(dp)