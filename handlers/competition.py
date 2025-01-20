from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import subprocess
import pandas as pd
import os
import importlib.util
import sys
from tasks.tasks import TASKS
from contextlib import redirect_stdout
import io
import json
from GigaChatHelper import get_hint

router = Router()

SOLVED_TASKS_FILE = "data/solved_tasks.json"

# Создаем файл для хранения решенных задач, если его нет
if not os.path.exists(SOLVED_TASKS_FILE):
    os.makedirs(os.path.dirname(SOLVED_TASKS_FILE), exist_ok=True)
    with open(SOLVED_TASKS_FILE, "w") as f:
        json.dump({}, f)

def get_solved_tasks(user_id: int) -> list:
    """Получить список решенных задач пользователя"""
    try:
        with open(SOLVED_TASKS_FILE, "r") as f:
            solved_tasks = json.load(f)
            return solved_tasks.get(str(user_id), [])
    except Exception:
        return []

def mark_task_solved(user_id: int, task_id: str):
    """Отметить задачу как решенную"""
    try:
        with open(SOLVED_TASKS_FILE, "r") as f:
            solved_tasks = json.load(f)
    except Exception:
        solved_tasks = {}
    
    if str(user_id) not in solved_tasks:
        solved_tasks[str(user_id)] = []
    
    if task_id not in solved_tasks[str(user_id)]:
        solved_tasks[str(user_id)].append(task_id)
        
        with open(SOLVED_TASKS_FILE, "w") as f:
            json.dump(solved_tasks, f)

def get_task_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками для каждой задачи"""
    keyboard = []
    solved = []  # Здесь можно добавить логику для отметки решенных задач
    
    for task_id, task in TASKS.items():
        status = "✅" if task_id in solved else "⭕️"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status} {task.title}",
                callback_data=f"task_{task_id}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(Command("tasks"))
async def cmd_tasks(message: types.Message):
    """Показать список доступных задач"""
    await message.answer(
        "📝 Выберите задачу для просмотра:",
        reply_markup=get_task_keyboard()
    )

@router.callback_query(F.data.startswith("task_"))
async def show_task_callback(callback: types.CallbackQuery):
    """Показать описание конкретной задачи"""
    task_id = callback.data[5:]  # Убираем префикс "task_"
    task = TASKS[task_id]
    solved = get_solved_tasks(callback.from_user.id)
    
    text = [
        f"📋 Задача: {task.title}",
        f"💎 Стоимость: {task.points} очков",
        f"Статус: {'✅ Решена' if task_id in solved else '⭕️ Не решена'}\n",
        task.description,
        "\n📝 Примеры:",
    ]
    
    for i, example in enumerate(task.examples, 1):
        text.append(f"Пример {i}:")
        text.append(f"Вход: {example['input']}")
        text.append(f"Выход: {example['output']}\n")
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📤 Отправить решение", callback_data=f"submit_{task_id}"),
                InlineKeyboardButton(text="💡 Подсказка", callback_data=f"hint_{task_id}")
            ],
            [InlineKeyboardButton(text="◀️ К списку задач", callback_data="back_to_tasks")]
        ]
    )
    
    await callback.message.edit_text("\n".join(text), reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "back_to_tasks")
async def back_to_tasks_callback(callback: types.CallbackQuery):
    """Вернуться к списку задач"""
    await cmd_tasks(callback.message)
    await callback.answer()

@router.callback_query(F.data.startswith("hint_"))
async def hint_task_callback(callback: types.CallbackQuery):
    """Показать подсказку для конкретной задачи"""
    task_id = callback.data[5:]  # Убираем префикс "hint_"
    task = TASKS[task_id]
    
    try:
        hint = get_hint(f"Подскажи как решить задачу: {task.description}")
        await callback.message.answer(f"💡 Подсказка к задаче '{task.title}':\n\n{hint}")
    except Exception as e:
        await callback.message.answer(
            "Попробуйте разбить задачу на подзадачи и решать их последовательно.\n"
            "Если у вас есть конкретный вопрос, используйте команду /hint"
        )
    await callback.answer()

@router.callback_query(F.data.startswith("submit_"))
async def submit_task_callback(callback: types.CallbackQuery):
    """Начать процесс отправки решения"""
    task_id = callback.data[7:]  # Убираем префикс "submit_"
    task = TASKS[task_id]
    
    await callback.message.answer(
        f"📤 Отправьте файл с решением задачи '{task.title}'.\n"
        f"Файл должен содержать функцию {task_id}() с нужной сигнатурой."
    )
    await callback.answer()

@router.message(Command("submit"))
async def cmd_submit(message: types.Message):
    """Начать процесс отправки решения"""
    await message.answer(
        "📤 Отправьте .py файл с вашим решением.\n"
        "⚠️ Файл должен содержать одну из следующих функций:\n"
        "- sum_array(arr)\n"
        "- find_max(arr)\n"
        "- is_prime(n)\n\n"
        "Используйте /tasks чтобы увидеть список задач."
    )

def check_solution(file_path: str) -> tuple[bool, str, str, int]:
    """Проверяет решение и возвращает (успех, сообщение, task_id, очки)"""
    try:
        # Загружаем модуль с решением
        spec = importlib.util.spec_from_file_location("solution", file_path)
        if not spec or not spec.loader:
            return False, "Ошибка загрузки решения", "", 0
        
        solution = importlib.util.module_from_spec(spec)
        sys.modules["solution"] = solution
        spec.loader.exec_module(solution)
        
        # Определяем, какая задача решается
        task_id = ""
        solution_func = None
        
        if hasattr(solution, "sum_array"):
            task_id = "sum_array"
            solution_func = solution.sum_array
        elif hasattr(solution, "find_max"):
            task_id = "find_max"
            solution_func = solution.find_max
        elif hasattr(solution, "is_prime"):
            task_id = "is_prime"
            solution_func = solution.is_prime
        else:
            return False, "Не найдена ни одна из требуемых функций", "", 0
        
        task = TASKS[task_id]
        
        # Проверяем на тестах
        for i, test in enumerate(task.test_cases, 1):
            # Перехватываем вывод функции
            f = io.StringIO()
            with redirect_stdout(f):
                result = solution_func(test["input"])
            
            if result != test["output"]:
                return False, f"Ошибка на тесте {i}:\nВход: {test['input']}\nОжидалось: {test['output']}\nПолучено: {result}", task_id, 0
        
        return True, "Все тесты пройдены!", task_id, task.points
        
    except Exception as e:
        return False, f"Ошибка при выполнении: {str(e)}", "", 0

@router.message(F.document)
async def handle_file(message: types.Message):
    if not message.document.file_name.endswith(".py"):
        await message.answer("Пожалуйста, отправьте файл с расширением .py")
        return

    file_path = f"submissions/{message.document.file_name}"
    os.makedirs("submissions", exist_ok=True)
    
    try:
        # Скачиваем файл
        file = await message.bot.get_file(message.document.file_id)
        await message.bot.download_file(file.file_path, file_path)
        
        # Проверяем решение
        success, result_message, task_id, points = check_solution(file_path)
        
        if success:
            # Проверяем, не решена ли уже эта задача
            solved_tasks = get_solved_tasks(message.from_user.id)
            if task_id in solved_tasks:
                await message.answer(
                    f"✅ Задача '{TASKS[task_id].title}' решена верно!\n"
                    "Но вы уже получили за неё очки ранее.\n\n"
                    "Используйте /tasks чтобы увидеть другие задачи"
                )
                return

            # Получаем имя пользователя
            user_name = ""
            with open("data/users.csv", "r", encoding='utf-8') as f:
                for line in f:
                    user_id, name, _ = line.strip().split(",")
                    if user_id == str(message.from_user.id):
                        user_name = name
                        break

            # Обновляем таблицу лидеров
            try:
                # Создаем или читаем таблицу лидеров
                if not os.path.exists("data/leaderboard.csv"):
                    os.makedirs(os.path.dirname("data/leaderboard.csv"), exist_ok=True)
                    with open("data/leaderboard.csv", "w", encoding='utf-8') as f:
                        f.write("name,score\n")
                    leaderboard = pd.DataFrame(columns=["name", "score"])
                else:
                    leaderboard = pd.read_csv("data/leaderboard.csv")

                # Проверяем и обновляем очки
                if user_name in leaderboard["name"].values:
                    mask = leaderboard["name"] == user_name
                    leaderboard.loc[mask, "score"] = leaderboard.loc[mask, "score"] + points
                else:
                    new_row = pd.DataFrame({"name": [user_name], "score": [points]})
                    leaderboard = pd.concat([leaderboard, new_row], ignore_index=True)

                # Сохраняем обновленную таблицу
                leaderboard.to_csv("data/leaderboard.csv", index=False, encoding='utf-8')
                
                # Отмечаем задачу как решенную
                mark_task_solved(message.from_user.id, task_id)
                
            except Exception as e:
                print(f"Error updating leaderboard: {e}")
                await message.answer("⚠️ Произошла ошибка при обновлении таблицы лидеров, но ваше решение засчитано!")

            await message.answer(
                f"✅ Задача '{TASKS[task_id].title}' решена верно!\n"
                f"Вы получили {points} очков! 🏆\n\n"
                f"Используйте /tasks чтобы увидеть другие задачи"
            )
        else:
            await message.answer(f"❌ {result_message}")
            
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка при проверке решения: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.message(Command("hint"))
async def cmd_hint(message: types.Message):
    user_message = message.text.replace("/hint", "").strip()
    if not user_message:
        await message.answer(
            "Пожалуйста, отправьте текст задания после команды /hint.\n"
            "Пример: /hint Напишите функцию, которая проверяет, является ли число простым."
        )
        return

    try:
        hint = get_hint(user_message) 
        await message.answer(f"Подсказка:\n{hint}")
    except Exception:
        await message.answer("Произошла ошибка при обработке запроса. Попробуйте позже.")


def register_handlers_competition(dp):
    dp.include_router(router)