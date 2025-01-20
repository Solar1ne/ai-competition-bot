import logging
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import register_handlers
from middlewares.auth import AuthMiddleware
from config import BOT_TOKEN

# Создаем директории если их нет
os.makedirs("data", exist_ok=True)
os.makedirs("submissions", exist_ok=True)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=storage)
scheduler = AsyncIOScheduler()

# Установка командного меню
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начало работы"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/tasks", description="Список задач"),
        BotCommand(command="/hint", description="Подсказка"),
        BotCommand(command="/register", description="Регистрация"),
        BotCommand(command="/leaderboard", description="Таблица лидеров"),
        BotCommand(command="/submit", description="Отправить решение"),
        BotCommand(command="/menu", description="Открыть меню"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Регистрация Middleware
    dp.message.middleware(AuthMiddleware())

    # Регистрация хэндлеров
    register_handlers(dp)

    # Установка команд
    await set_commands(bot)

    # Запуск планировщика
    scheduler.start()

    # Запуск бота
    logger.info("Starting bot...")
    try:
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
                "edited_message",
                "callback_query",
                "inline_query",
                "chosen_inline_result",
            ],
            skip_updates=True
        )
    except Exception as e:
        logger.error(f"Error while polling: {e}")
    finally:
        await bot.session.close()
        scheduler.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")