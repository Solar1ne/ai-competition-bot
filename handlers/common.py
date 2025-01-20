from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from handlers.competition import cmd_tasks, cmd_submit
from handlers.leaderboard import cmd_leaderboard

router = Router()

def get_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру с кнопками"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Меню"), 
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True
    )

def get_inline_menu() -> InlineKeyboardMarkup:
    """Создает inline-меню с кнопками"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Список задач", callback_data="show_tasks"),
                InlineKeyboardButton(text="📤 Отправить решение", callback_data="show_submit")
            ],
            [
                InlineKeyboardButton(text="📊 Таблица лидеров", callback_data="show_leaderboard"),
                InlineKeyboardButton(text="💡 Подсказка", callback_data="show_hint")
            ]
        ]
    )

@router.message(F.text == "📝 Меню")
@router.message(Command("menu"))
async def show_menu(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=get_inline_menu())

@router.message(F.text == "❓ Помощь")
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
📋 <b>Доступные команды:</b>

/start - Начать работу с ботом
/register - Зарегистрироваться в системе
/help - Показать это сообщение
/tasks - Посмотреть список доступных задач
/submit - Отправить решение задачи
/leaderboard - Посмотреть таблицу лидеров

<b>Как пользоваться ботом:</b>
1. Сначала зарегистрируйтесь командой /register
2. Посмотрите список задач через /tasks
3. Выберите задачу и изучите её условие
4. Отправьте решение через /submit
5. Следите за своим прогрессом в /leaderboard

За каждую решённую задачу вы получаете очки! 🏆
"""
    await message.answer(help_text, reply_markup=get_keyboard())

# Обработчики callback-кнопок
@router.callback_query(F.data == "show_tasks")
async def show_tasks_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    await cmd_tasks(callback.message)
    await callback.answer()

@router.callback_query(F.data == "show_submit")
async def show_submit_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    await cmd_submit(callback.message)
    await callback.answer()

@router.callback_query(F.data == "show_leaderboard")
async def show_leaderboard_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    await cmd_leaderboard(callback.message)
    await callback.answer()

@router.callback_query(F.data == "show_hint")
async def show_hint_callback(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "💡 Чтобы получить подсказку, используйте команду /hint и опишите свой вопрос.\n"
        "Например: /hint Как найти сумму элементов массива?"
    )
    await callback.answer()

def register_handlers_common(dp):
    dp.include_router(router) 