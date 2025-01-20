from aiogram import types, Router, F, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
import os
from handlers.common import get_inline_menu, get_keyboard

# Создаем роутер
router = Router()

# Машина состояний для регистрации
class RegistrationState(StatesGroup):
    NAME = State()
    EMAIL = State()

def is_user_registered(user_id: int) -> tuple[bool, str]:
    """Проверяет регистрацию пользователя и возвращает его имя если зарегистрирован"""
    if not os.path.exists("data/users.csv"):
        return False, ""
        
    try:
        with open("data/users.csv", "r", encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    id_, name, _ = line.strip().split(",")
                    if str(user_id) == id_:
                        return True, name
    except Exception as e:
        print(f"Error checking registration: {e}")
    return False, ""

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    is_registered, name = is_user_registered(message.from_user.id)
    greeting = f"С возвращением, {name}!\n\n" if is_registered else "👋 Привет! Добро пожаловать в бота для соревнований!\n\n"
    
    text_parts = [
        greeting,
        "🔹 Здесь вы можете решать задачи и получать очки",
        "🔹 Соревнуйтесь с другими участниками",
        "🔹 Следите за своим прогрессом в таблице лидеров\n",
    ]
    
    if is_registered:
        text_parts.append("Выберите действие в меню ниже:")
    else:
        text_parts.extend([
            "Для начала нажмите кнопку 'Регистрация'",
            "Или используйте команду: /register"
        ])
    
    await message.answer("\n".join(text_parts), reply_markup=get_keyboard())

@router.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    is_registered, name = is_user_registered(message.from_user.id)
    
    if is_registered:
        await message.answer(f"Вы уже зарегистрированы как {name}! ✅\nИспользуйте /help для просмотра доступных команд.")
        return
        
    await state.clear()  # Clear any existing state
    await message.answer("Введите ваше имя:")
    await state.set_state(RegistrationState.NAME)

@router.message(StateFilter(RegistrationState.NAME), ~F.text.startswith("/"))
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш email:")
    await state.set_state(RegistrationState.EMAIL)

@router.message(StateFilter(RegistrationState.EMAIL), ~F.text.startswith("/"))
async def process_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["email"] = message.text

    # Создаем директорию если её нет
    os.makedirs("data", exist_ok=True)

    # Проверяем, не зарегистрирован ли уже пользователь
    is_registered, _ = is_user_registered(message.from_user.id)
    if is_registered:
        await message.answer("Вы уже зарегистрированы!")
        await state.clear()
        return

    # Перезаписываем файл без дубликатов
    users = []
    if os.path.exists("data/users.csv"):
        with open("data/users.csv", "r", encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    id_, name, email = line.strip().split(",")
                    if id_ != str(message.from_user.id):  # Пропускаем существующие записи для этого пользователя
                        users.append((id_, name, email))

    # Добавляем новую запись
    users.append((str(message.from_user.id), data['name'], data['email']))

    # Сохраняем обновленный список
    with open("data/users.csv", "w", encoding='utf-8') as file:
        for user in users:
            file.write(f"{user[0]},{user[1]},{user[2]}\n")

    success_message = [
        f"Вы успешно зарегистрированы как {data['name']}! ✅\n",
        "Теперь вы можете:",
        "📤 Отправлять решения через /submit",
        "📊 Следить за прогрессом в /leaderboard\n",
        "Используйте /help для просмотра всех команд"
    ]
    
    await message.answer("\n".join(success_message))
    await state.clear()

def register_handlers_start(dp: Dispatcher):
    dp.include_router(router)