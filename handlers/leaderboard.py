from aiogram import types, Router
from aiogram.filters import Command
import pandas as pd
import os

router = Router()

@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: types.Message):
    try:
        # Проверяем существование файла и его содержимое
        if not os.path.exists("data/leaderboard.csv") or os.path.getsize("data/leaderboard.csv") == 0:
            # Создаем файл с заголовками если он пустой
            with open("data/leaderboard.csv", "w") as f:
                f.write("name,score\n")
            await message.answer("Таблица лидеров пуста.")
            return

        # Читаем таблицу лидеров
        leaderboard = pd.read_csv("data/leaderboard.csv")
        
        if len(leaderboard) == 0:
            await message.answer("Таблица лидеров пуста.")
            return
            
        # Сортируем по очкам
        leaderboard = leaderboard.sort_values(by="score", ascending=False)
        
        # Формируем текст сообщения
        text = "🏆 Таблица лидеров:\n\n"
        for i, row in leaderboard.iterrows():
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "👤"
            text += f"{medal} {i+1}. {row['name']} — {row['score']} очков\n"
        
        await message.answer(text)
        
    except Exception as e:
        await message.answer("Произошла ошибка при загрузке таблицы лидеров.")
        print(f"Error in leaderboard: {e}")

def register_handlers_leaderboard(dp):
    dp.include_router(router)